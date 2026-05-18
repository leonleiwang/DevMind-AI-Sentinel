from typing import Dict, Any, List

from app.mcp.servers.base import BaseMCPServer
from app.mcp.servers.prometheus_server import PrometheusMCPServer
from app.mcp.servers.jira_server import JiraMCPServer
from app.mcp.servers.gitlab_server import GitLabMCPServer
from app.mcp.servers.confluence_server import ConfluenceMCPServer
from app.mcp.servers.incident_server import IncidentMCPServer


class MCPManager:
    """
    MCP 管理器：负责根据配置初始化所有 MCP Server 实例，并暴露统一的工具列表与调用接口。
    """

    def __init__(self, server_configs: dict):
        self.servers: Dict[str, BaseMCPServer] = {}
        self._init_servers(server_configs)

    def _init_servers(self, configs: dict):
        # 只初始化配置中 enabled=True 的服务器
        for name, cfg in configs.items():
            if not cfg.get("enabled", False):
                continue

            if name == "prometheus":
                self.servers[name] = PrometheusMCPServer(cfg)
            elif name == "jira":
                self.servers[name] = JiraMCPServer(cfg)
            elif name == "gitlab":          # 新增
                self.servers[name] = GitLabMCPServer(cfg)
            elif name == "confluence":
                self.servers[name] = ConfluenceMCPServer(cfg)
            elif name == "incident":
                self.servers[name] = IncidentMCPServer(cfg)
            # 后续可扩展 gitlab、confluence 等
            # elif name == "gitlab":
            #     self.servers[name] = GitLabMCPServer(cfg)
            # elif name == "confluence":
            #     self.servers[name] = DocMCPServer(cfg)

    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有已注册 MCP Server 的全部工具列表（带来源信息）"""
        tools = []
        for server in self.servers.values():
            for tool in await server.list_tools():
                tool["server"] = server.name
                tools.append(tool)
        return tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Any:
        """调用指定服务器上的工具"""
        server = self.servers.get(server_name)
        if not server:
            raise ValueError(f"MCP Server '{server_name}' not found or not enabled")
        return await server.call_tool(tool_name, arguments)
