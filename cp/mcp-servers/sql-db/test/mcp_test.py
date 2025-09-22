import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from faker import Faker

# Import the necessary service(s) here
from sbilifeco.models.base import Response
from sbilifeco.boundaries.sql_db import ISqlDb
from sbilifeco.cp.sql_db.mcp.server import SqlDbMCPServer
from sbilifeco.cp.common.mcp.client import MCPClient


class SqlDbMcpTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        self.faker = Faker()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        if self.test_type == "unit":
            http_port = int(
                getenv(EnvVars.http_port_unittest, Defaults.http_port_unittest)
            )
        else:
            http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.sql_db = AsyncMock(spec=ISqlDb)
        self.execute_query = patch.object(
            self.sql_db,
            "execute_query",
            AsyncMock(return_value=Response.ok([{"number": 1}])),
        ).start()

        self.service = SqlDbMCPServer().set_sql_db(self.sql_db).set_http_port(http_port)
        await self.service.async_init()
        await self.service.listen()

        # Initialise the client(s) here
        self.client = MCPClient().set_server_url(f"http://localhost:{http_port}/mcp")
        await self.client.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()
        await self.service.async_shutdown()
        patch.stopall()

    async def test_get_tools(self) -> None:
        # Act
        tools_response = await self.client.get_tools()

        # Assert
        self.assertTrue(tools_response.is_success)
        assert tools_response.payload is not None

        tool = next(iter(tools_response.payload))
        assert tool is not None

        self.assertEqual(tool.name, "sql_executor")
        self.assertEqual(
            tool.description, "Executes a SQL query and returns the result"
        )

    async def test_execute_query(self) -> None:
        # Arrange
        query = self.faker.sentence()

        # Act
        result = await self.client.call_tool("sql_executor", {"query": query})

        self.execute_query.assert_awaited_once_with(query)

        # Assert
        assert result is not None
        self.assertFalse(result.is_error)

        assert result.structured_content is not None
        self.assertIn("result", result.structured_content)
        self.assertEqual(result.structured_content.get("result"), [{"number": 1}])
