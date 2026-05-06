import random
from typing import Any, Dict, List

from app.mcp.servers.base import BaseMCPServer


class PrometheusMCPServer(BaseMCPServer):
    """
    模拟 Prometheus MCP Server。
    提供查询指标、查看告警两个工具。
    """

    def __init__(self, config: dict):
        super().__init__("prometheus", config)

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "query_prometheus_metric",
                "description": "Execute a PromQL query to retrieve a metric value at the current moment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "PromQL query string, e.g. 'up{job=\"api-server\"}'"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_active_alerts",
                "description": "List all currently firing alerts in Prometheus.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name == "query_prometheus_metric":
            query = arguments.get("query", "")
            # 模拟返回随机指标值
            return {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {
                            "metric": {"instance": "localhost:9090", "job": "api-server"},
                            "value": [1620000000, str(random.uniform(0, 100))]
                        }
                    ]
                }
            }
        elif tool_name == "list_active_alerts":
            # 模拟返回一些常见告警
            return {
                "status": "success",
                "data": {
                    "alerts": [
                        {
                            "labels": {"alertname": "HighCPUUsage", "severity": "warning"},
                            "annotations": {"summary": "CPU usage above 80%"},
                            "state": "firing",
                            "activeAt": "2025-05-05T08:00:00Z"
                        },
                        {
                            "labels": {"alertname": "DiskSpaceLow", "severity": "critical"},
                            "annotations": {"summary": "Disk space on /data is below 10%"},
                            "state": "firing",
                            "activeAt": "2025-05-05T07:30:00Z"
                        }
                    ]
                }
            }
        else:
            raise ValueError(f"Unknown tool: {tool_name}")