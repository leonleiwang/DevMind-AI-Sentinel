# backend/app/agent/supervisor.py
from langgraph.graph import END, START, StateGraph

from app.agent.fault_diagnosis import FaultDiagnosisAgent
from app.agent.incident_analysis import IncidentAnalysisAgent
from app.agent.prompts import SUPERVISOR_PROMPT
from app.core.llm import get_llm
from app.mcp.manager import MCPManager


def classify_intent(user_message: str) -> str:
    """
    独立的意图识别函数，返回 fault / incident / code / doc / unknown。
    """
    llm = get_llm()
    response = llm.invoke(SUPERVISOR_PROMPT.format(user_input=user_message))
    intent = response.content.strip().lower()
    if intent not in ["fault", "incident", "code", "doc"]:
        intent = "unknown"
    return intent


def create_supervisor_graph(mcp_manager: MCPManager):
    """
    构建主管 Agent 状态图（保留，供后续扩展完整多 Agent 流程）。
    当前主要接口仍在各 API 路由中直接调用对应 Agent。
    """
    fault_agent = FaultDiagnosisAgent(mcp_manager)
    incident_agent = IncidentAnalysisAgent(mcp_manager)

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
            "intermediate_steps": result["intermediate_steps"],
        }

    def _run_incident_agent(state):
        import asyncio

        query = state["messages"][-1].content
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        result = loop.run_until_complete(incident_agent.run(query))
        return {
            "final_output": result["output"],
            "intermediate_steps": result["intermediate_steps"],
        }

    def _run_default(_state):
        return {
            "final_output": (
                "我可以处理故障排查、事故 RCA、代码审查和文档问答。"
                "请补充你要分析的服务、时间范围或问题类型。"
            )
        }

    def _route_intent(state):
        intent = state.get("intent", "unknown")
        if intent == "fault":
            return "fault_agent"
        if intent == "incident":
            return "incident_agent"
        return "default"

    graph = StateGraph(dict)
    graph.add_node("classify_intent", _classify_intent)
    graph.add_node("fault_agent", _run_fault_agent)
    graph.add_node("incident_agent", _run_incident_agent)
    graph.add_node("default", _run_default)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        _route_intent,
        {
            "fault_agent": "fault_agent",
            "incident_agent": "incident_agent",
            "default": "default",
        },
    )
    graph.add_edge("fault_agent", END)
    graph.add_edge("incident_agent", END)
    graph.add_edge("default", END)

    return graph.compile()
