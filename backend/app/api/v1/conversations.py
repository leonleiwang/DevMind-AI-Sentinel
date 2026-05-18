# backend/app/api/v1/conversations.py
import json
import asyncio
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.agent.supervisor import classify_intent          # 独立意图识别
from app.agent.fault_diagnosis import FaultDiagnosisAgent
from app.agent.incident_analysis import IncidentAnalysisAgent
from app.mcp.manager import MCPManager
from app.core.config import settings

router = APIRouter()

# 全局 MCP 管理器和故障排查 Agent
mcp_manager = MCPManager(settings.MCP_SERVER_CONFIGS)
fault_agent = FaultDiagnosisAgent(mcp_manager)
incident_agent = IncidentAnalysisAgent(mcp_manager)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


@router.post("/stream")
async def chat_stream(
    chat_input: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    async def event_generator():
        # 1. 意图识别
        intent = classify_intent(chat_input.message)
        yield {
            "event": "intent",
            "data": json.dumps({"intent": intent}, ensure_ascii=False)
        }
        await asyncio.sleep(0.5)

        # 2. 根据意图处理
        if intent == "fault":
            # 运行故障排查 Agent
            result = await fault_agent.run(chat_input.message)
        elif intent == "incident":
            result = await incident_agent.run(chat_input.message)
        else:
            result = None

        if result:
            steps = result.get("intermediate_steps", [])
            for step in steps:
                # 思考
                yield {
                    "event": "thought",
                    "data": json.dumps({"content": step.get("thought", "")}, ensure_ascii=False)
                }
                # 工具调用
                yield {
                    "event": "action",
                    "data": json.dumps({
                        "tool": step.get("action", ""),
                        "input": step.get("action_input", {})
                    }, ensure_ascii=False)
                }
                # 观察结果
                yield {
                    "event": "observation",
                    "data": json.dumps({"content": step.get("observation", "")}, ensure_ascii=False)
                }
                await asyncio.sleep(0.3)
            # 最终结论
            yield {
                "event": "final",
                "data": json.dumps({"content": result.get("output", "")}, ensure_ascii=False)
            }
        else:
            yield {
                "event": "final",
                "data": json.dumps({
                    "content": (
                        "我还不能确定你要处理什么任务。请补充服务名、时间范围或问题类型，"
                        "例如：'分析今天 13:00 订单服务故障的根因' 或 '查看网关延迟告警'。"
                    )
                }, ensure_ascii=False)
            }

    return EventSourceResponse(event_generator())
