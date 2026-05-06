# backend/app/agent/code_review.py
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
        result = await self.agent.ainvoke(inputs)
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