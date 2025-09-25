import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from typing import Annotated

# Import the necessary service(s) here
from sbilifeco.cp.common.mcp.client import MCPClient
from sbilifeco.cp.common.mcp.server import MCPServer


class ServerImpl(MCPServer):
    def create_tools(self):
        super().create_tools()

        @self.tool(
            name="say_hello",
            description="A simple tool that says hello to the given name.",
        )
        async def say_hello(
            name_of_greeted: Annotated[
                str, "The name of the person to greet."
            ] = "There",
        ) -> str:
            return f"Hello, {name_of_greeted}!"


class Test(IsolatedAsyncioTestCase):
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
        self.server = ServerImpl().set_http_port(http_port)
        await self.server.async_init()
        await self.server.listen()

        self.client = MCPClient().set_server_url(f"http://localhost:{http_port}/mcp")
        await self.client.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # await self.service.async_shutdown()
        ...

    async def test_get_tools(self):
        response = await self.client.get_tools()

        self.assertTrue(response.is_success)
        assert response.payload is not None

        hello_tool = next(iter(response.payload))
        self.assertEqual(hello_tool.name, "say_hello")
        self.assertEqual(
            hello_tool.description, "A simple tool that says hello to the given name."
        )

        assert "properties" in hello_tool.inputSchema
        self.assertIn("name_of_greeted", hello_tool.inputSchema["properties"])
        self.assertIn("type", hello_tool.inputSchema["properties"]["name_of_greeted"])
        param_name_of_greeted = hello_tool.inputSchema["properties"]["name_of_greeted"]

        self.assertEqual(param_name_of_greeted["type"], "string")
        self.assertIn(
            "description",
            param_name_of_greeted,
        )
        self.assertEqual(
            param_name_of_greeted["description"],
            "The name of the person to greet.",
        )

    async def test_say_hello(self) -> None:
        # Arrange
        async with self.client:
            # Act
            response = await self.client.call_tool(
                "say_hello", {"name_of_greeted": "World"}
            )

            # Assert
            self.assertTrue(response)
            self.assertEqual(response.data, "Hello, World!")

    async def test_fetch_tools(self) -> None:
        # Arrange

        # Act
        list_of_tools = await self.client.fetch_tools()

        # Assert
        self.assertTrue(list_of_tools)
        tool = next(iter(list_of_tools))
        self.assertEqual(tool.name, "say_hello")
        self.assertEqual(
            tool.description,
            "A simple tool that says hello to the given name.",
        )

        param = next(iter(tool.params))
        self.assertEqual(param.name, "name_of_greeted")
        self.assertEqual(param.description, "The name of the person to greet.")
        self.assertEqual(param.type, "string")
        self.assertFalse(param.is_required)

    async def test_invoke_tool(self) -> None:
        # Arrange
        tool_name = "say_hello"
        name_argument = "Tester"

        # Act
        result = await self.client.invoke_tool(tool_name, name_of_greeted=name_argument)

        # Assert
        self.assertTrue(result)
        self.assertIn("result", result)
        self.assertEqual(result["result"], f"Hello, {name_argument}!")
