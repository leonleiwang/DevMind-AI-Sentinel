"""
作为临时测试接口（无需认证，方便调试）
"""

from fastapi import APIRouter, HTTPException
from app.mcp.manager import MCPManager
from app.core.config import settings

router = APIRouter()

# 初始化一个全局 MCPManager 实例（真正的生产环境会用依赖注入）
mcp_manager = MCPManager(settings.MCP_SERVER_CONFIGS)


@router.get("/tools")
async def list_available_tools():
    tools = await mcp_manager.list_all_tools()
    return tools


@router.post("/call")
async def call_mcp_tool(server: str, tool: str, args: dict = {}):
    try:
        result = await mcp_manager.call_tool(server, tool, args)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))