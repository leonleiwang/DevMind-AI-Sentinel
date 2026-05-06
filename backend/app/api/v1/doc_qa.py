# backend/app/api/v1/doc_qa.py
import json, asyncio
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.agent.doc_qa import DocQAAgent
from app.mcp.manager import MCPManager
from app.core.config import settings

router = APIRouter()
mcp_manager = MCPManager(settings.MCP_SERVER_CONFIGS)
doc_agent = DocQAAgent(mcp_manager)

class DocQARequest(BaseModel):
    message: str

@router.post("/stream")
async def doc_qa_stream(request: DocQARequest, current_user=Depends(get_current_user)):
    async def event_generator():
        yield {"event": "intent", "data": json.dumps({"intent": "doc_qa"}, ensure_ascii=False)}
        await asyncio.sleep(0.3)
        result = await doc_agent.run(request.message)
        steps = result.get("intermediate_steps", [])
        for step in steps:
            yield {"event": "thought", "data": json.dumps({"content": step["thought"]}, ensure_ascii=False)}
            yield {"event": "action", "data": json.dumps({"tool": step["action"], "input": step["action_input"]}, ensure_ascii=False)}
            yield {"event": "observation", "data": json.dumps({"content": step["observation"]}, ensure_ascii=False)}
            await asyncio.sleep(0.2)
        yield {"event": "final", "data": json.dumps({"content": result["output"]}, ensure_ascii=False)}
    return EventSourceResponse(event_generator())