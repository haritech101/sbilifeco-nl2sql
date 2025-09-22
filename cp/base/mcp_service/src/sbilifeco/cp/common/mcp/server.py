from __future__ import annotations
from fastmcp import FastMCP
from uvicorn import Config, Server


class MCPServer(FastMCP):
    def __init__(self):
        self.server_name = "Unknown MCP Server"
        self.server_instructions = ""
        self.http_host = "0.0.0.0"
        self.http_port = 80

    def set_server_name(self, server_name: str) -> MCPServer:
        self.server_name = server_name
        return self

    def set_server_instructions(self, server_instructions: str) -> MCPServer:
        self.server_instructions = server_instructions
        return self

    def set_http_host(self, http_host: str) -> MCPServer:
        self.http_host = http_host
        return self

    def set_http_port(self, http_port: int) -> MCPServer:
        self.http_port = http_port
        return self

    async def async_init(self):
        FastMCP.__init__(
            self, name=self.server_name, instructions=self.server_instructions
        )
        self.create_tools()

    async def listen(self) -> None:
        config = Config(
            app=self.http_app(transport="http"),
            host=self.http_host,
            port=self.http_port,
            log_level="info",
        )
        config.load()

        self.server = Server(config=config)
        self.server.lifespan = config.lifespan_class(config)
        await self.server.startup()

    async def stop(self) -> None:
        await self.server.shutdown()

    def create_tools(self):
        pass
