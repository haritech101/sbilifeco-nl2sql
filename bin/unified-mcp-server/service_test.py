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
from service import UnifiedMCPMicroservice
from sbilifeco.cp.common.mcp.client import MCPClient
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        mcp_url = getenv(EnvVars.mcp_url, Defaults.mcp_url)

        population_counter_proto = getenv(
            EnvVars.population_counter_proto, Defaults.population_counter_proto
        )
        population_counter_host = getenv(
            EnvVars.population_counter_host, Defaults.population_counter_host
        )
        population_counter_port = int(
            getenv(EnvVars.population_counter_port, Defaults.population_counter_port)
        )

        # Initialise the service(s) here
        self.faker = Faker()
        self.key = self.faker.word()
        self.division = self.faker.word()

        if self.test_type == "unit":
            self.service = UnifiedMCPMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.mcp_client = MCPClient()
        (self.mcp_client.set_server_url(mcp_url))
        await self.mcp_client.async_init()

        self.http_client = SessionDataManagerHttpClient()
        (
            self.http_client.set_proto(population_counter_proto)
            .set_host(population_counter_host)
            .set_port(population_counter_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        await self.http_client.delete_session_data(f"{self.key}::{self.division}")
        patch.stopall()

    async def test_count(self) -> None:
        # Arrange
        count = randint(1, 100)

        await self.http_client.update_session_data(
            f"{self.key}::{self.division}", f"{count}"
        )

        # Act
        response = await self.mcp_client.invoke_tool(
            "count_by_named_division", key=self.key, division_name=self.division
        )

        # Assert
        assert response is not None
        self.assertEqual(response, {"is_success": True, "count": count})
