from __future__ import annotations
from typing import Any
from fastmcp import Client
from mcp.types import Tool as Tool
from fastmcp.client.transports import StreamableHttpTransport
from sbilifeco.models.base import Response


class MCPClient:
    def __init__(self):
        self.server_url = "http://localhost/mcp"

    def set_server_url(self, url: str) -> MCPClient:
        self.server_url = url
        return self

    async def async_init(self):
        self.client = Client(StreamableHttpTransport(url=self.server_url))

    async def get_tools(self) -> Response[list[Tool]]:
        async with self.client:
            try:
                return Response.ok(await self.client.list_tools())
            except Exception as e:
                return Response.error(e)
