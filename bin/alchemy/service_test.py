import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from service import AlchemyMicroservice
from sbilifeco.cp.common.mcp.client import MCPClient


class AlchemyMicroserviceTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        if self.test_type == "unit":
            self.service = AlchemyMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client = MCPClient()
        self.client.set_server_url(
            f"http://{"tech101.in" if self.test_type == "staging" else "localhost"}:{http_port}/mcp"
        )
        await self.client.async_init()

    async def asyncTearDown(self) -> None: ...

    async def test_get_tools(self) -> None:
        list_of_tools = await self.client.fetch_tools()
        self.assertGreater(len(list_of_tools), 0)

        tool = next(iter(list_of_tools))
        self.assertIsNotNone(tool)
        self.assertIn("sql", tool.name)

    async def test_basic_query(self) -> None:
        # Arrange
        query = "SELECT 1 AS number"

        # Act
        mcp_response = await self.client.invoke_tool("sql_executor", query=query)

        # Assert
        self.assertTrue(mcp_response)
        self.assertIn("result", mcp_response)

        content = mcp_response.get("result")
        self.assertEqual(content, [{"number": 1}], content)

    async def test_relevant_query(self) -> None:
        # Arrange
        query = "SELECT * from dim_region"

        # Act
        mcp_response = await self.client.invoke_tool("sql_executor", query=query)

        # Assert
        self.assertTrue(mcp_response)
        self.assertIn("result", mcp_response)

        records = mcp_response.get("result")
        assert type(records) is list
        self.assertGreater(len(records), 0)

        record = records[0]
        assert type(record) is dict
        for k in record:
            self.assertIsNotNone(k)
