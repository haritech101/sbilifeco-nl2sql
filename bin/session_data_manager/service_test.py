import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from session_data_manager import ServiceDataManagerExecutable
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from faker import Faker
from uuid import uuid4


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".local/.env")
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        self.service = ServiceDataManagerExecutable()
        await self.service.run()

        self.http_client = SessionDataManagerHttpClient()
        self.http_client.set_port(http_port).set_host("localhost").set_proto("http")

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        await self.http_client.delete_all_session_data()

    async def test_set_and_delete(self) -> None:
        # Arrange
        session_id = uuid4().hex
        data = self.faker.paragraph()

        # Act
        update_response = await self.http_client.update_session_data(session_id, data)

        # Assert
        self.assertTrue(update_response.is_success, update_response.message)

        fetch_response = await self.http_client.get_session_data(session_id)
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        self.assertEqual(fetch_response.payload, data)

        # Act
        delete_response = await self.http_client.delete_session_data(session_id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)

        fetch_response_after_delete = await self.http_client.get_session_data(
            session_id
        )
        self.assertTrue(
            fetch_response_after_delete.is_success, fetch_response_after_delete.message
        )
        self.assertEqual(fetch_response_after_delete.payload, "")
