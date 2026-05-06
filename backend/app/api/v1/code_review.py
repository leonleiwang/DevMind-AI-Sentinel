# backend/app/api/v1/code_review.py
import json
import asyncio
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.agent.code_review import CodeReviewAgent
from app.mcp.manager import MCPManager
from app.core.config import settings

router = APIRouter()
mcp_manager = MCPManager(settings.MCP_SERVER_CONFIGS)
code_review_agent = CodeReviewAgent(mcp_manager)


class ReviewRequest(BaseModel):
    message: str = "请审查当前所有待处理的合并请求"


@router.post("/stream")
async def code_review_stream(
    review_input: ReviewRequest,
    current_user=Depends(get_current_user)
):
    async def event_generator():
        yield {"event": "intent", "data": json.dumps({"intent": "code_review"}, ensure_ascii=False)}
        await asyncio.sleep(0.3)

        result = await code_review_agent.run(review_input.message)
        steps = result.get("intermediate_steps", [])
        for step in steps:
            yield {"event": "thought", "data": json.dumps({"content": step.get("thought", "")}, ensure_ascii=False)}
            yield {"event": "action", "data": json.dumps({"tool": step.get("action", ""), "input": step.get("action_input", {})}, ensure_ascii=False)}
            yield {"event": "observation", "data": json.dumps({"content": step.get("observation", "")}, ensure_ascii=False)}
            await asyncio.sleep(0.2)
        yield {"event": "final", "data": json.dumps({"content": result.get("output", "")}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())