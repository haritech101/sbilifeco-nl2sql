import http
import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from service import SessionDataManagerMicroservice
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from sbilifeco.cp.population_counter.http_client import PopulationCounterHttpClient
from faker import Faker
from uuid import uuid4
from random import randint


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".local/.env")
        test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port_session_data = int(
            getenv(EnvVars.http_port_session_data, Defaults.http_port_session_data)
        )
        http_port_population = int(
            getenv(EnvVars.http_port_population, Defaults.http_port_population)
        )

        if test_type == "unit":
            self.service = SessionDataManagerMicroservice()
            await self.service.run()

        self.http_client_session_data = SessionDataManagerHttpClient()
        self.http_client_session_data.set_port(http_port_session_data).set_host(
            "localhost"
        ).set_proto("http")

        self.http_client_population = PopulationCounterHttpClient()
        self.http_client_population.set_port(http_port_population).set_host(
            "localhost"
        ).set_proto("http")

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        await self.http_client_session_data.delete_all_session_data()

    async def test_set_and_delete(self) -> None:
        # Arrange
        session_id = uuid4().hex
        data = self.faker.paragraph()

        # Act
        update_response = await self.http_client_session_data.update_session_data(
            session_id, data
        )

        # Assert
        self.assertTrue(update_response.is_success, update_response.message)

        fetch_response = await self.http_client_session_data.get_session_data(
            session_id
        )
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        self.assertEqual(fetch_response.payload, data)

        # Act
        delete_response = await self.http_client_session_data.delete_session_data(
            session_id
        )

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)

        fetch_response_after_delete = (
            await self.http_client_session_data.get_session_data(session_id)
        )
        self.assertTrue(
            fetch_response_after_delete.is_success, fetch_response_after_delete.message
        )
        self.assertEqual(fetch_response_after_delete.payload, "")

    async def test_count_by_named_division(self) -> None:
        # Arrange
        key = self.faker.word()
        division = self.faker.word()
        num_entries = randint(1, 10)

        await self.http_client_session_data.update_session_data(
            f"{key}::{division}", str(num_entries)
        )

        # Act
        response = await self.http_client_population.count_by_named_division(
            key, division
        )

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertEqual(response.payload, num_entries)
