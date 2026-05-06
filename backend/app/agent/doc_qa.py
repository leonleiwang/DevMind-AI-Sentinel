# backend/app/agent/doc_qa.py
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.mcp.tools import get_langchain_tools
from app.mcp.manager import MCPManager

DOC_QA_PROMPT = """你是一个企业技术文档问答 Agent。你可以使用工具搜索 Confluence 知识库，并基于检索到的文档回答用户问题。

{tools}

规则：
- 必须使用 search_documents 工具搜索相关文档，再根据文档内容回答。
- 如果文档中没有明确答案，如实告知并建议联系相关团队。
- 回答时引用文档标题（或文档 ID）。

请用以下格式输出：
Thought: ...
Action: ...
Action Input: ...
Observation: ...
Final Answer: ...

现在开始回答用户问题："""


class DocQAAgent:
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.llm = get_llm()
        self.agent = None
        self.tools = None

    async def initialize(self):
        self.tools = await get_langchain_tools(
            self.mcp_manager,
            server_filter=["confluence"]
        )
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        tool_names = ", ".join([t.name for t in self.tools])

        system_text = DOC_QA_PROMPT.format(
            tools=tool_descriptions,
            tool_names=tool_names
        )
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_text
        )

    async def run(self, user_query: str):
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