import json
from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model

from app.mcp.manager import MCPManager


def json_schema_to_pydantic(schema: dict, model_name: str = "ArgsSchema") -> type[BaseModel]:
    """
    将简单的 JSON Schema 转换为 Pydantic 模型，用于 LangChain 工具的参数校验。
    这是一个简易版本，只支持最常用的 string/object 类型。
    """
    fields = {}
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    for field_name, field_info in properties.items():
        f_type = str  # 默认字符串
        default = ... if field_name in required else None
        fields[field_name] = (f_type, default)

    # 使用 pydantic create_model 动态生成
    if not fields:
        # 如果没有参数，创建一个空的 Pydantic 模型
        return create_model(model_name)
    return create_model(model_name, **fields)


async def get_langchain_tools(mcp_manager: MCPManager, server_filter: List[str] = None) -> List[StructuredTool]:
    """
    从 MCP 管理器获取所有工具，并转换为 LangChain 能直接使用的 StructuredTool 列表。
    可选 server_filter 只转换特定服务器的工具。
    """
    langchain_tools = []
    all_tools = await mcp_manager.list_all_tools()

    for tool_info in all_tools:
        server_name = tool_info["server"]
        if server_filter and server_name not in server_filter:
            continue

        tool_name = tool_info["name"]
        description = tool_info.get("description", "")
        parameters = tool_info.get("parameters", {})

        # 创建参数 Pydantic 模型
        args_schema = json_schema_to_pydantic(parameters, f"{tool_name}_args")

        # 为了循环内捕获正确的 server_name / tool_name，需要做工厂函数
        def make_callable(srv, tname):
            async def _call_tool(**kwargs):
                # 调用 MCP 管理器的方法
                result = await mcp_manager.call_tool(srv, tname, kwargs)
                # 返回字符串格式，方便 LLM 阅读
                return json.dumps(result, ensure_ascii=False, indent=2)
            return _call_tool

        tool = StructuredTool(
            name=tool_name,
            description=description,
            args_schema=args_schema,
            coroutine=make_callable(server_name, tool_name),
        )
        langchain_tools.append(tool)

    return langchain_tools