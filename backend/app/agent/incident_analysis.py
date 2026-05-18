# backend/app/agent/incident_analysis.py
import json
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.prompts import INCIDENT_ANALYSIS_PROMPT
from app.core.llm import get_llm
from app.mcp.manager import MCPManager
from app.mcp.tools import get_langchain_tools


class IncidentAnalysisAgent:
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.llm = get_llm()
        self.agent = None
        self.tools = None

    async def initialize(self):
        self.tools = await get_langchain_tools(
            self.mcp_manager,
            server_filter=["incident"],
        )
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])

        system_text = INCIDENT_ANALYSIS_PROMPT.format(tools=tool_descriptions)
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_text,
        )

    async def run(self, user_query: str):
        if not self.agent:
            await self.initialize()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_message = f"当前时间: {current_time}\n用户事故描述: {user_query}"
        try:
            result = await self.agent.ainvoke({"messages": [HumanMessage(content=user_message)]})
        except Exception as exc:
            return await self._run_fallback(user_query, exc)

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
                        "observation": "",
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
            "intermediate_steps": intermediate_steps,
        }

    async def _run_fallback(self, user_query: str, error: Exception):
        timeline_result = await self.mcp_manager.call_tool(
            "incident",
            "get_incident_timeline",
            {"incident_time": user_query, "service": "order-service"},
        )
        timeline = timeline_result.get("timeline", [])
        observation = json.dumps(timeline_result, ensure_ascii=False, indent=2)

        timeline_lines = "\n".join(
            [
                f"- {event['time']} [{event['source']}] {event['service']}: {event['event']}"
                for event in timeline
            ]
        )
        final_output = f"""1. 事件时间线
{timeline_lines}

2. 可能根因
订单服务 v2.3.1 发布后触发数据库连接池耗尽，导致 API 网关 P95 延迟上升，并伴随 CPU 使用率升高。由于回滚后延迟恢复，部署变更与故障恢复之间存在强关联。

3. 关键证据
- 13:18 开始发布 v2.3.1，13:20 CPU 升至 95%。
- 13:21 P95 延迟从 200ms 升至 2.5s。
- 13:22 出现 Database connection pool exhausted。
- 13:30 触发回滚，13:35 延迟恢复到 260ms。

4. 影响范围
主要影响 order-service 及依赖它的 api-gateway，请求延迟显著升高，可能造成订单创建、查询等链路超时。

5. 建议动作
- 保持回滚版本稳定运行，暂停 v2.3.1 继续发布。
- 检查 v2.3.1 的数据库连接池配置、连接释放逻辑和重试策略。
- 对比发布前后连接池大小、超时时间、慢查询和数据库最大连接数。

6. 后续预防措施
- 为连接池耗尽、P95 延迟和部署事件建立关联告警。
- 灰度发布阶段加入自动回滚阈值。
- 在发布前增加连接池配置检查和压测用例。

备注：当前 LLM 调用失败，已切换为基于模拟 MCP 时间线的离线 RCA 兜底分析。错误类型：{type(error).__name__}"""

        return {
            "output": final_output,
            "intermediate_steps": [
                {
                    "thought": "LLM 暂时不可用，切换到离线 RCA 兜底流程，直接读取 Incident Timeline MCP 数据。",
                    "action": "get_incident_timeline",
                    "action_input": {"incident_time": user_query, "service": "order-service"},
                    "observation": observation,
                }
            ],
        }
