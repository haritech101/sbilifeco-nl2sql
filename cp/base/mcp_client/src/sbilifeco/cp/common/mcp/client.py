from __future__ import annotations
from datetime import timedelta
from typing import Any
from fastmcp import Client
from fastmcp.client.client import CallToolResult
from fastmcp.client.progress import ProgressHandler
from mcp.types import Tool as Tool, CallToolResult as ToolResult
from fastmcp.client.transports import StreamableHttpTransport
from sbilifeco.models.base import Response
from sbilifeco.boundaries.tool_support import (
    IExternalToolRepo,
    ExternalTool,
    ExternalToolParams,
)


class MCPClient(Client, IExternalToolRepo):
    DEFAULT_URL = "http://localhost/mcp"

    def __init__(self):
        super().__init__(self.DEFAULT_URL)
        self.server_url = self.DEFAULT_URL

    def set_server_url(self, url: str) -> MCPClient:
        self.server_url = url
        return self

    async def async_init(self):
        self.transport = StreamableHttpTransport(url=self.server_url)

    async def async_shutdown(self): ...

    async def get_tools(self) -> Response[list[Tool]]:
        async with self:
            try:
                return Response.ok(await self.list_tools())
            except Exception as e:
                return Response.error(e)

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        timeout: timedelta | float | int | None = None,
        progress_handler: ProgressHandler | None = None,
        raise_on_error: bool = True,
    ) -> CallToolResult:
        async with self:
            return await super().call_tool(
                name, arguments, timeout, progress_handler, raise_on_error
            )

    async def fetch_tools(self) -> list[ExternalTool]:
        try:
            response = await self.get_tools()

            if not response.is_success:
                print(response.message)
                return []
            if not response.payload:
                print("List of tools came up empty")
                return []

            return [
                ExternalTool(
                    name=tool.name,
                    description=tool.description or "Tool hasn't been described",
                    params=[
                        ExternalToolParams(
                            name=param_name,
                            type=param_details.get("type", "string"),
                            description=param_details.get(
                                "description", "No description provided"
                            ),
                            is_required=(
                                param_name in tool.inputSchema.get("required", [])
                            ),
                        )
                        for param_name, param_details in tool.inputSchema.get(
                            "properties", {}
                        ).items()
                    ],
                )
                for tool in response.payload
            ]
        except Exception as e:
            return []

    async def invoke_tool(self, tool_name: str, **kwargs) -> dict:
        try:
            result = await self.call_tool(tool_name, kwargs)
            if not result.structured_content:
                print(f"No content returned from tool {tool_name}")
                return {}

            return result.structured_content
        except Exception as e:
            print(f"Error invoking tool {tool_name}: {e}")
            return {}
