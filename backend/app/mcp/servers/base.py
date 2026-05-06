from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseMCPServer(ABC):
    """
    MCP 服务器的抽象基类。
    所有具体实现的服务器（Prometheus、GitLab 等）都要继承它。
    """

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        返回该服务器提供的工具列表。
        每条工具记录需包含：
        - name: 工具名称
        - description: 描述
        - parameters: JSON Schema 格式的参数定义（可选）
        """
        ...

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用指定工具并返回结果。
        """
        ...