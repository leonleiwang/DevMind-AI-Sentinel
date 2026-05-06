# backend/app/mcp/servers/gitlab_server.py
from typing import Any, Dict, List
from app.mcp.servers.base import BaseMCPServer

# 模拟的合并请求数据
MOCK_MERGE_REQUESTS = [
    {
        "id": 1,
        "title": "修复订单服务超时 Bug",
        "description": "增加数据库连接超时重试逻辑",
        "author": "张三",
        "changes": [
            {"file": "order_service.py", "diff": "+ retry_on_timeout(max_retries=3)\n- # no retry\n+ connection_pool_size = 50"},
            {"file": "config.yaml", "diff": "+ timeout: 30s\n- timeout: 5s"}
        ]
    },
    {
        "id": 2,
        "title": "新增用户认证中间件",
        "description": "实现 JWT 验证中间件并接入全站路由",
        "author": "李四",
        "changes": [
            {"file": "auth_middleware.py", "diff": "+ def verify_jwt(token): ...\n+ app.add_middleware(AuthMiddleware)"}
        ]
    }
]


class GitLabMCPServer(BaseMCPServer):
    def __init__(self, config: dict):
        super().__init__("gitlab", config)

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_merge_request_changes",
                "description": "获取指定合并请求的代码变更详情，包括修改的文件和差异内容。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mr_id": {"type": "integer", "description": "合并请求 ID"}
                    },
                    "required": ["mr_id"]
                }
            },
            {
                "name": "list_merge_requests",
                "description": "列出所有待审查的合并请求。",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "post_review_comment",
                "description": "在指定的合并请求中发布审查评论。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mr_id": {"type": "integer", "description": "合并请求 ID"},
                        "file": {"type": "string", "description": "评论所在的文件路径"},
                        "line": {"type": "integer", "description": "评论所在的行号"},
                        "comment": {"type": "string", "description": "评论内容"}
                    },
                    "required": ["mr_id", "comment"]
                }
            }
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name == "get_merge_request_changes":
            mr_id = int(arguments.get("mr_id", 0))   # 强制转 int
            mr = next((m for m in MOCK_MERGE_REQUESTS if m["id"] == mr_id), None)
            if not mr:
                return {"error": "Merge request not found"}
            return mr

        elif tool_name == "list_merge_requests":
            return {"merge_requests": [{"id": m["id"], "title": m["title"], "author": m["author"]} for m in MOCK_MERGE_REQUESTS]}

        elif tool_name == "post_review_comment":
            return {
                "status": "posted",
                "mr_id": arguments.get("mr_id"),
                "comment": arguments.get("comment"),
                "file": arguments.get("file", "unknown"),
                "line": arguments.get("line", 1)
            }

        else:
            raise ValueError(f"Unknown GitLab tool: {tool_name}")