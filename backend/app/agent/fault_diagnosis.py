# backend/app/agent/fault_diagnosis.py
from datetime import datetime
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.llm import get_llm
from app.mcp.tools import get_langchain_tools
from app.mcp.manager import MCPManager
from app.agent.prompts import FAULT_DIAGNOSIS_PROMPT


class FaultDiagnosisAgent:
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.llm = get_llm()
        self.agent = None
        self.tools = None

    async def initialize(self):
        # 获取工具（带过滤）
        self.tools = await get_langchain_tools(
            self.mcp_manager,
            server_filter=["prometheus", "jira"]
        )

        # 准备工具列表文本，用于填充系统提示（只含静态内容）
        tool_descriptions = "\n".join(
            [f"- {t.name}: {t.description}" for t in self.tools]
        )
        tool_names = ", ".join([t.name for t in self.tools])

        # 动态内容（当前时间、用户输入）不在此处写入，留在运行时注入
        system_text = FAULT_DIAGNOSIS_PROMPT.format(
            tools=tool_descriptions,
            tool_names=tool_names
        )

        # 使用 langchain.agents.create_agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_text
        )

    async def run(self, user_query: str):
        if not self.agent:
            await self.initialize()

        # 动态注入当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 将时间和用户问题组合成一条 HumanMessage
        user_message = f"当前时间: {current_time}\n用户问题: {user_query}"

        inputs = {"messages": [HumanMessage(content=user_message)]}

        # 调用 Agent
        result = await self.agent.ainvoke(inputs)

        # 从消息列表中提取最终答案和中间步骤
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
                    # 寻找紧随其后的 ToolMessage
                    for j in range(i + 1, len(messages)):
                        follow = messages[j]
                        if hasattr(follow, "tool_call_id") and follow.tool_call_id == tc["id"]:
                            step["observation"] = follow.content
                            break
                    intermediate_steps.append(step)
            elif not (hasattr(msg, "tool_calls") and msg.tool_calls):
                # 纯文本 AIMessage 作为最终输出
                final_output = msg.content

        return {
            "output": final_output,
            "intermediate_steps": intermediate_steps
        }