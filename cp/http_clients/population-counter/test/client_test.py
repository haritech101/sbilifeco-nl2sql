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
from sbilifeco.boundaries.population_counter import IPopulationCounter
from sbilifeco.cp.population_counter.http_client import PopulationCounterHttpClient
from sbilifeco.cp.population_counter.http_server import PopulationCounterHttpServer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.service = AsyncMock(spec=IPopulationCounter)
        self.http_server = (
            PopulationCounterHttpServer()
            .set_population_counter(self.service)
            .set_http_port(http_port)
        )
        await self.http_server.listen()

        # Initialise the client(s) here
        self.client = PopulationCounterHttpClient()
        (self.client.set_proto("http").set_host("localhost").set_port(http_port))

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.http_server.stop()
        patch.stopall()

    async def test_count_by_named_division(self) -> None:
        # Arrange
        key = self.faker.word()
        division = self.faker.word()
        count_by_named_division = patch.object(
            self.service, "count_by_named_division", return_value=Response.ok(0)
        ).start()

        # Act
        response = await self.client.count_by_named_division(key, division)

        # Assert
        self.assertTrue(response.is_success, response.message)
        count_by_named_division.assert_called_once_with(key, division)

    async def test_count_by_numeric_range(self) -> None:
        # Arrange
        key = self.faker.word()
        min = randint(1, 50)
        max = randint(51, 100)
        count_by_numeric_range = patch.object(
            self.service, "count_by_numeric_range", return_value=Response.ok(0)
        ).start()

        # Act
        response = await self.client.count_by_numeric_range(key, min, max)

        # Assert
        self.assertTrue(response.is_success, response.message)
        count_by_numeric_range.assert_called_once_with(key, min, max)

    async def test_count_by_date_range(self) -> None:
        # Arrange
        key = self.faker.word()
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        count_by_date_range = patch.object(
            self.service, "count_by_date_range", return_value=Response.ok(0)
        ).start()

        # Act
        response = await self.client.count_by_date_range(key, start_date, end_date)

        # Assert
        self.assertTrue(response.is_success, response.message)
        count_by_date_range.assert_called_once_with(key, start_date, end_date)

    async def test_count_by_boolean_flag(self) -> None:
        # Arrange
        key = self.faker.word()
        truth = self.faker.boolean()
        count_by_boolean = patch.object(
            self.service, "count_by_boolean", return_value=Response.ok(0)
        ).start()

        # Act
        response = await self.client.count_by_boolean(key, truth)

        # Assert
        self.assertTrue(response.is_success, response.message)
        count_by_boolean.assert_called_once_with(key, truth)
