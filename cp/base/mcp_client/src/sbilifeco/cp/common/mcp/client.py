from __future__ import annotations
from datetime import timedelta
from typing import Any
from fastmcp import Client
from fastmcp.client.client import CallToolResult
from fastmcp.client.progress import ProgressHandler
from mcp.types import Tool as Tool, CallToolResult as ToolResult
from fastmcp.client.transports import StreamableHttpTransport
from sbilifeco.models.base import Response


class MCPClient(Client):
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
