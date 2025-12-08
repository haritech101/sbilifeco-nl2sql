from typing import Protocol
from pydantic import BaseModel


class ExternalToolParams(BaseModel):
    name: str
    description: str
    type: str = "string"
    is_required: bool = False


class ExternalTool(BaseModel):
    name: str
    description: str
    params: list[ExternalToolParams] = []
    example_usage: str = ""


class IExternalToolRepo(Protocol):
    async def fetch_tools(self) -> list[ExternalTool]:
        raise NotImplementedError("This method should be overridden by subclasses")

    async def invoke_tool(self, tool_name: str, **kwargs) -> dict:
        raise NotImplementedError("This method should be overridden by subclasses")
