# backend/app/agent/supervisor.py
from langgraph.graph import StateGraph, END, START
from app.core.llm import get_llm
from app.agent.fault_diagnosis import FaultDiagnosisAgent
from app.mcp.manager import MCPManager


def classify_intent(user_message: str) -> str:
    """
    独立的意图识别函数，直接返回标签。
    """
    llm = get_llm()
    prompt = f"""你是一个智能运维平台的主控 Agent。
用户的输入是: {user_message}
请判断意图属于: fault（故障排查）、code（代码审查）、doc（文档问答）、unknown（无关）。
只返回一个单词。"""
    response = llm.invoke(prompt)
    intent = response.content.strip().lower()
    if intent not in ["fault", "code", "doc"]:
        intent = "unknown"
    return intent


def create_supervisor_graph(mcp_manager: MCPManager):
    """
    构建主管 Agent 的状态图（保留，供未来扩展完整多 Agent 流程）。
    现在并未直接使用，但保留以备后续整合。
    """
    llm = get_llm()
    fault_agent = FaultDiagnosisAgent(mcp_manager)

    # 图内部的意图识别（这里复用独立函数）
    def _classify_intent(state):
        last_msg = state["messages"][-1].content
        return {"intent": classify_intent(last_msg)}

    def _run_fault_agent(state):
        import asyncio
        query = state["messages"][-1].content
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fault_agent.run(query))
        return {
            "final_output": result["output"],
            "intermediate_steps": result["intermediate_steps"]
        }

    def _run_default(state):
        return {"final_output": "我只能处理故障排查、代码审查和文档问答，请重新描述您的问题。"}

    def _route_intent(state):
        intent = state.get("intent", "unknown")
        if intent == "fault":
            return "fault_agent"
        return "default"

    graph = StateGraph(dict)
    graph.add_node("classify_intent", _classify_intent)
    graph.add_node("fault_agent", _run_fault_agent)
    graph.add_node("default", _run_default)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges("classify_intent", _route_intent, {
        "fault_agent": "fault_agent",
        "default": "default"
    })
    graph.add_edge("fault_agent", END)
    graph.add_edge("default", END)

    return graph.compile()