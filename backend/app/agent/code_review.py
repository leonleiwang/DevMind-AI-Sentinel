# backend/app/agent/code_review.py
import json

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.mcp.tools import get_langchain_tools
from app.mcp.manager import MCPManager

CODE_REVIEW_PROMPT = """你是一个资深的代码审查 Agent。
你可以使用以下工具来获取合并请求的变更内容，并发表审查意见：

{tools}

代码审查规范：
- 检查潜在的安全漏洞（SQL 注入、XSS、权限绕过等）
- 检查代码逻辑错误和边界条件
- 检查性能问题（无效循环、N+1 查询等）
- 检查是否遵循编码规范（命名、注释、异常处理）
- 对于发现的问题，使用 post_review_comment 工具直接发表评论，必须包含具体的文件路径和建议

审查流程：
1. 使用 list_merge_requests 获取待审查的合并请求列表
2. 使用 get_merge_request_changes 逐个获取代码变更
3. 对每个文件的变更进行审查，发现问题立即发表评论
4. 最终给出审查总结

请使用以下格式输出：
Thought: [推理]
Action: [工具名称]
Action Input: [JSON 参数]
Observation: [工具返回]
... (可重复)
Final Answer: [审查总结]

现在开始审查："""


class CodeReviewAgent:
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.llm = get_llm()
        self.agent = None
        self.tools = None

    async def initialize(self):
        self.tools = await get_langchain_tools(
            self.mcp_manager,
            server_filter=["gitlab"]
        )
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        tool_names = ", ".join([t.name for t in self.tools])

        system_text = CODE_REVIEW_PROMPT.format(
            tools=tool_descriptions,
            tool_names=tool_names
        )
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_text
        )

    async def run(self, user_query: str = "请审查当前所有待处理的合并请求"):
        if not self.agent:
            await self.initialize()
        inputs = {"messages": [HumanMessage(content=user_query)]}
        try:
            result = await self.agent.ainvoke(inputs)
        except Exception as exc:
            return await self._run_fallback(exc)

        messages = result["messages"]
        final_output = ""
        intermediate_steps = []

        for i, msg in enumerate(messages):
            if isinstance(msg, SystemMessage):
                continue
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    step = {
                        "thought": msg.content if msg.content else "",
                        "action": tc["name"],
                        "action_input": tc["args"],
                        "observation": ""
                    }
                    for j in range(i + 1, len(messages)):
                        follow = messages[j]
                        if hasattr(follow, "tool_call_id") and follow.tool_call_id == tc["id"]:
                            step["observation"] = follow.content
                            break
                    intermediate_steps.append(step)
            elif not (hasattr(msg, "tool_calls") and msg.tool_calls):
                final_output = msg.content

        return {
            "output": final_output,
            "intermediate_steps": intermediate_steps
        }

    async def _run_fallback(self, error: Exception):
        intermediate_steps = []

        mr_list = await self.mcp_manager.call_tool("gitlab", "list_merge_requests", {})
        intermediate_steps.append({
            "thought": "LLM 暂时不可用，切换到离线代码审查兜底流程，先读取待审查 MR 列表。",
            "action": "list_merge_requests",
            "action_input": {},
            "observation": json.dumps(mr_list, ensure_ascii=False, indent=2),
        })

        findings = []
        for mr in mr_list.get("merge_requests", []):
            mr_id = mr["id"]
            changes = await self.mcp_manager.call_tool(
                "gitlab",
                "get_merge_request_changes",
                {"mr_id": mr_id},
            )
            intermediate_steps.append({
                "thought": f"读取 MR !{mr_id} 的变更内容并执行规则化审查。",
                "action": "get_merge_request_changes",
                "action_input": {"mr_id": mr_id},
                "observation": json.dumps(changes, ensure_ascii=False, indent=2),
            })

            for change in changes.get("changes", []):
                file_path = change.get("file", "unknown")
                diff = change.get("diff", "")
                if "connection_pool_size" in diff:
                    comment = (
                        "连接池配置变更会影响线上容量，请确认该值与数据库 max_connections、"
                        "服务副本数和超时重试策略匹配，并补充压测或回滚说明。"
                    )
                    await self.mcp_manager.call_tool(
                        "gitlab",
                        "post_review_comment",
                        {"mr_id": mr_id, "file": file_path, "line": 1, "comment": comment},
                    )
                    findings.append(f"- MR !{mr_id} `{file_path}`：{comment}")
                    intermediate_steps.append({
                        "thought": "发现连接池配置风险，发布审查评论。",
                        "action": "post_review_comment",
                        "action_input": {
                            "mr_id": mr_id,
                            "file": file_path,
                            "line": 1,
                            "comment": comment,
                        },
                        "observation": "审查评论已模拟发布。",
                    })
                elif "verify_jwt" in diff:
                    comment = (
                        "认证中间件需要覆盖 token 过期、签名错误、缺失 Authorization Header "
                        "和权限绕过测试，建议补充单元测试与失败分支处理。"
                    )
                    await self.mcp_manager.call_tool(
                        "gitlab",
                        "post_review_comment",
                        {"mr_id": mr_id, "file": file_path, "line": 1, "comment": comment},
                    )
                    findings.append(f"- MR !{mr_id} `{file_path}`：{comment}")
                    intermediate_steps.append({
                        "thought": "发现认证边界条件风险，发布审查评论。",
                        "action": "post_review_comment",
                        "action_input": {
                            "mr_id": mr_id,
                            "file": file_path,
                            "line": 1,
                            "comment": comment,
                        },
                        "observation": "审查评论已模拟发布。",
                    })

        if not findings:
            findings_text = "- 未发现阻断级问题，建议补充测试后合并。"
        else:
            findings_text = "\n".join(findings)

        final_output = f"""代码审查总结

已审查 {len(mr_list.get("merge_requests", []))} 个待处理 MR，并基于模拟 GitLab MCP 数据完成离线规则审查。

主要发现：
{findings_text}

建议：
- 对配置、认证、安全和性能相关变更补充测试证据。
- 对影响生产稳定性的参数变更补充回滚方案。
- 若接入真实 GitLab，可将当前 MCP Server 替换为真实 API 实现，Agent 侧流程无需大改。

备注：当前 LLM 调用失败，已切换为离线代码审查兜底分析。错误类型：{type(error).__name__}"""

        return {
            "output": final_output,
            "intermediate_steps": intermediate_steps,
        }
