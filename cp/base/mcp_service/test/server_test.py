import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbilifeco.cp.common.mcp.server import MCPServer
from fastmcp import Client


class MCPServerImpl(MCPServer):
    def create_tools(self):
        super().create_tools()

        @self.tool(
            name="Say Hello", description="Says hello to the user, given their name."
        )
        async def say_hello(name: str) -> str:
            return f"Hello, {name}!"


class MCPServerTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        if self.test_type == "unit":
            http_port = int(
                getenv(EnvVars.http_port_unittest, Defaults.http_port_unittest)
            )
        else:
            http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialize the service(s) here
        if self.test_type == "unit":
            self.service = MCPServerImpl().set_http_port(http_port)
            await self.service.async_init()
            await self.service.listen()

        self.client = Client(f"http://localhost:{http_port}/mcp")

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()

    async def test_ping(self) -> None:
        # Arrange
        async with self.client:
            # Act
            response = await self.client.ping()

            # Assert
            self.assertTrue(response)

    async def test_list_tools(self) -> None:
        # Arrange
        async with self.client:
            # Act
            tools = await self.client.list_tools()

            # Assert
            self.assertTrue(tools, tools)

            tool = tools[0]
            self.assertEqual(tool.name, "Say Hello")
            self.assertEqual(
                tool.description, "Says hello to the user, given their name."
            )

    async def test_say_hello(self) -> None:
        # Arrange
        name = "Greg"
        async with self.client:
            # Act
            response = await self.client.call_tool("Say Hello", {"name": name})

            # Assert
            self.assertEqual(response.data, f"Hello, {name}!")
