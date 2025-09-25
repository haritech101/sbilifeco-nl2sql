from typing import Protocol
from pydantic import BaseModel


class ExternalTool(BaseModel):
    name: str
    description: str
    example_usage: str = ""


class IExternalToolRepo(Protocol):
    async def fetch_tools(self) -> list[ExternalTool]:
        raise NotImplementedError("This method should be overridden by subclasses")

    async def invoke_tool(self, tool_name: str, **kwargs) -> dict:
        raise NotImplementedError("This method should be overridden by subclasses")
