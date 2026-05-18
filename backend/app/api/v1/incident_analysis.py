# backend/app/api/v1/incident_analysis.py
import asyncio
import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.agent.incident_analysis import IncidentAnalysisAgent
from app.api.deps import get_current_user
from app.core.config import settings
from app.mcp.manager import MCPManager

router = APIRouter()

mcp_manager = MCPManager(settings.MCP_SERVER_CONFIGS)
incident_agent = IncidentAnalysisAgent(mcp_manager)


class IncidentAnalysisRequest(BaseModel):
    message: str
    conversation_id: str = "incident-default"


@router.post("/stream")
async def incident_analysis_stream(
    request: IncidentAnalysisRequest,
    current_user=Depends(get_current_user),
):
    async def event_generator():
        yield {
            "event": "intent",
            "data": json.dumps({"intent": "incident"}, ensure_ascii=False),
        }
        await asyncio.sleep(0.2)

        result = await incident_agent.run(request.message)
        steps = result.get("intermediate_steps", [])
        for step in steps:
            yield {
                "event": "thought",
                "data": json.dumps({"content": step.get("thought", "")}, ensure_ascii=False),
            }
            yield {
                "event": "action",
                "data": json.dumps(
                    {
                        "tool": step.get("action", ""),
                        "input": step.get("action_input", {}),
                    },
                    ensure_ascii=False,
                ),
            }
            yield {
                "event": "observation",
                "data": json.dumps({"content": step.get("observation", "")}, ensure_ascii=False),
            }
            await asyncio.sleep(0.2)

        yield {
            "event": "final",
            "data": json.dumps({"content": result.get("output", "")}, ensure_ascii=False),
        }

    return EventSourceResponse(event_generator())
