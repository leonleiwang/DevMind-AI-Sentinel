from typing import Any, Dict, List

from app.mcp.servers.base import BaseMCPServer


MOCK_TIMELINE = [
    {
        "time": "13:18",
        "event": "Deployment v2.3.1 started rolling out to production",
        "source": "CI/CD",
        "service": "order-service",
        "severity": "info",
    },
    {
        "time": "13:20",
        "event": "CPU usage spiked to 95%",
        "source": "Prometheus",
        "service": "order-service",
        "severity": "warning",
    },
    {
        "time": "13:21",
        "event": "P95 latency jumped from 200ms to 2.5s",
        "source": "Prometheus",
        "service": "api-gateway",
        "severity": "critical",
    },
    {
        "time": "13:22",
        "event": "Database connection pool exhausted",
        "source": "PostgreSQL logs",
        "service": "order-service",
        "severity": "critical",
    },
    {
        "time": "13:25",
        "event": "Deployment v2.3.1 completed on all production pods",
        "source": "CI/CD",
        "service": "order-service",
        "severity": "info",
    },
    {
        "time": "13:30",
        "event": "On-call engineer triggered rollback",
        "source": "Incident Management",
        "service": "order-service",
        "severity": "info",
    },
    {
        "time": "13:35",
        "event": "P95 latency recovered to 260ms after rollback",
        "source": "Prometheus",
        "service": "api-gateway",
        "severity": "info",
    },
]


class IncidentMCPServer(BaseMCPServer):
    """
    模拟 Incident Timeline MCP Server。
    用于 RCA 演示：把部署、指标、数据库日志和事件管理记录统一成时间线。
    """

    def __init__(self, config: dict):
        super().__init__("incident", config)

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_incident_timeline",
                "description": (
                    "Return a simulated incident timeline with deployment events, "
                    "metric anomalies, database errors and mitigation actions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "incident_time": {
                            "type": "string",
                            "description": "Approximate incident time, e.g. 'today 13:00' or '13:20'.",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service name, e.g. 'order-service'.",
                        },
                    },
                    "required": [],
                },
            }
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name != "get_incident_timeline":
            raise ValueError(f"Unknown incident tool: {tool_name}")

        service = (arguments.get("service") or "").strip().lower()
        events = MOCK_TIMELINE
        if service:
            events = [
                event
                for event in MOCK_TIMELINE
                if service in event["service"].lower() or service in event["event"].lower()
            ]

        return {
            "incident_time": arguments.get("incident_time") or "13:00-14:00",
            "service_filter": arguments.get("service") or "all",
            "timeline": events,
            "summary": "Simulated production incident timeline for RCA demonstration.",
        }
