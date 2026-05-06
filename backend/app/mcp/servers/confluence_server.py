# backend/app/mcp/servers/confluence_server.py
from typing import Any, Dict, List
from app.mcp.servers.base import BaseMCPServer
from app.rag.vectorstore import get_vectorstore

class ConfluenceMCPServer(BaseMCPServer):
    def __init__(self, config: dict):
        super().__init__("confluence", config)
        self.vectorstore = get_vectorstore()

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_documents",
                "description": "在 Confluence 知识库中语义搜索相关技术文档。输入一个自然语言查询，返回最相关的文档片段。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "自然语言查询，如 '订单服务部署参数'"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name == "search_documents":
            query = arguments.get("query", "")
            # 语义搜索 top 3
            docs = self.vectorstore.similarity_search(query, k=3)
            results = []
            for doc in docs:
                results.append({
                    "id": doc.metadata.get("id", ""),
                    "title": doc.metadata.get("title", ""),
                    "content": doc.page_content[:500]  # 截取前500字符，避免上下文过长
                })
            return {"documents": results}
        else:
            raise ValueError(f"Unknown Confluence tool: {tool_name}")