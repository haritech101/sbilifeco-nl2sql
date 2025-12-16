import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.cp.common.mcp.client import MCPClient
from sbilifeco.cp.unified_mcp_server import UnifiedMCPServer
from sbilifeco.boundaries.population_counter import IPopulationCounter


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        mcp_port = int(getenv(EnvVars.mcp_port, Defaults.mcp_port))
        mcp_url = getenv(EnvVars.mcp_url, Defaults.mcp_url)

        # Initialise the service(s) here
        self.faker = Faker()

        self.gateway = AsyncMock(spec=IPopulationCounter)

        self.mcp_server = UnifiedMCPServer().set_population_counter(self.gateway)
        (self.mcp_server.set_population_counter(self.gateway).set_http_port(mcp_port))
        await self.mcp_server.async_init()
        await self.mcp_server.listen()

        # Initialise the client(s) here
        self.client = MCPClient()
        (self.client.set_server_url(mcp_url))
        await self.client.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.mcp_server.stop()
        await self.mcp_server.async_shutdown()
        patch.stopall()

    async def test_get_tools(self) -> None:
        # Act
        tools = await self.client.fetch_tools()

        # Assert
        self.assertIn("count_by_named_division", [tool.name for tool in tools])

    async def test_count_by_named_division(self) -> None:
        # Arrange
        count = randint(0, 1000)
        key = self.faker.word()
        division_name = self.faker.word()
        fn_count = patch.object(
            self.gateway,
            "count_by_named_division",
            AsyncMock(return_value=Response.ok(count)),
        ).start()

        # Act
        response = await self.client.invoke_tool(
            "count_by_named_division", key=key, division_name=division_name
        )

        # Assert
        assert response is not None
        fn_count.assert_called_once_with(key, division_name)
        self.assertEqual(response.get("is_success"), True)
        self.assertEqual(response.get("count"), count)

    async def test_count_by_numeric_range(self) -> None:
        # Arrange
        count = randint(0, 1000)
        key = self.faker.word()
        min_value = randint(0, 500)
        max_value = randint(501, 1000)
        fn_count = patch.object(
            self.gateway,
            "count_by_numeric_range",
            AsyncMock(return_value=Response.ok(count)),
        ).start()

        # Act
        response = await self.client.invoke_tool(
            "count_by_numeric_range",
            key=key,
            min_value=min_value,
            max_value=max_value,
        )

        # Assert
        assert response is not None
        fn_count.assert_called_once_with(key, min_value, max_value)
        self.assertEqual(response.get("is_success"), True)
        self.assertEqual(response.get("count"), count)

    async def test_count_by_date_range(self) -> None:
        # Arrange
        count = randint(0, 1000)
        key = self.faker.word()
        start_date = date(2023, 5, 1)
        end_date = date(2023, 5, 31)
        fn_count = patch.object(
            self.gateway,
            "count_by_date_range",
            AsyncMock(return_value=Response.ok(count)),
        ).start()

        # Act
        response = await self.client.invoke_tool(
            "count_by_date_range",
            key=key,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        # Assert
        assert response is not None
        fn_count.assert_called_once_with(key, start_date, end_date)
        self.assertEqual(response.get("is_success"), True)
        self.assertEqual(response.get("count"), count)

    async def test_count_by_boolean(self) -> None:
        # Arrange
        count = randint(0, 1000)
        key = self.faker.word()
        true_or_false = self.faker.boolean()
        fn_count = patch.object(
            self.gateway,
            "count_by_boolean",
            AsyncMock(return_value=Response.ok(count)),
        ).start()

        # Act
        response = await self.client.invoke_tool(
            "count_by_boolean",
            key=key,
            true_or_false=true_or_false,
        )

        # Assert
        assert response is not None
        fn_count.assert_called_once_with(key, true_or_false)
        self.assertEqual(response.get("is_success"), True)
        self.assertEqual(response.get("count"), count)
