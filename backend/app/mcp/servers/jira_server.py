# backend/app/mcp/servers/jira_server.py
from typing import Any, Dict, List
import datetime
from app.mcp.servers.base import BaseMCPServer

# 模拟用数据（后续可替换为真实 API）
MOCK_ISSUES = [
    {"id": "DEV-101", "summary": "订单服务响应超时", "status": "In Progress", "assignee": "张三"},
    {"id": "DEV-102", "summary": "数据库连接池耗尽", "status": "Open", "assignee": "李四"},
    {"id": "DEV-103", "summary": "内存泄漏告警", "status": "Done", "assignee": "王五"},
]

class JiraMCPServer(BaseMCPServer):
    def __init__(self, config: dict):
        super().__init__("jira", config)
        self.url = config.get("url", "")
        self.project_key = config.get("project_key", "DEVMIND")

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_jira_issues",
                "description": "根据关键词和状态搜索 Jira 工单。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "status": {"type": "string", "description": "工单状态，可选 Open, In Progress, Done", "default": "Open"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_jira_issue",
                "description": "创建一个新的 Jira 工单。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string", "description": "工单摘要"},
                        "description": {"type": "string", "description": "详细描述"},
                        "assignee": {"type": "string", "description": "指派给谁", "default": "未分配"}
                    },
                    "required": ["summary", "description"]
                }
            }
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name == "search_jira_issues":
            query = arguments.get("query", "").lower()
            status = arguments.get("status")
            results = []
            for issue in MOCK_ISSUES:
                if query in issue["summary"].lower():
                    if status is None or issue["status"] == status:
                        results.append(issue)
            return {"issues": results}
        elif tool_name == "create_jira_issue":
            new_id = f"DEV-{100 + len(MOCK_ISSUES) + 1}"
            new_issue = {
                "id": new_id,
                "summary": arguments["summary"],
                "status": "Open",
                "assignee": arguments.get("assignee", "未分配")
            }
            MOCK_ISSUES.append(new_issue)
            return {"issue": new_issue, "message": "工单创建成功"}
        else:
            raise ValueError(f"Unknown Jira tool: {tool_name}")