import http
import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from faker import Faker
from uuid import uuid4

# Import the necessary service(s) here
from sbilifeco.cp.session_data_manager.microservice import (
    SessionDataManagerMicroservice,
)
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.models.base import Response


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".local/.env")

        # Initialize the service(s) here
        self.gateway: ISessionDataManager = AsyncMock(spec=ISessionDataManager)

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        self.microservice = SessionDataManagerMicroservice()
        self.microservice.set_session_data_manager(self.gateway).set_http_port(
            http_port
        )

        await self.microservice.listen()

        self.http_client = SessionDataManagerHttpClient()
        self.http_client.set_host("localhost").set_proto("http").set_port(http_port)

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        await self.microservice.stop()

    async def test_update_session_data(self) -> None:
        # Arrange
        patched_update_method = patch.object(
            self.gateway, "update_session_data", return_value=Response.ok(None)
        ).start()

        # Act
        session_id = str(uuid4())
        session_data = self.faker.paragraph()

        update_response = await self.http_client.update_session_data(
            session_id, session_data
        )

        # Assert
        self.assertTrue(update_response.is_success)
        patched_update_method.assert_called_once_with(session_id, session_data)

    async def test_delete_session_data(self) -> None:
        # Arrange
        patched_delete_method = patch.object(
            self.gateway, "delete_session_data", return_value=Response.ok(None)
        ).start()
        session_id = str(uuid4())

        # Act
        delete_response = await self.http_client.delete_session_data(session_id)

        # Assert
        self.assertTrue(delete_response.is_success)
        patched_delete_method.assert_called_once_with(session_id)

    async def test_delete_all_session_data(self) -> None:
        # Arrange
        patched_delete_all_method = patch.object(
            self.gateway, "delete_all_session_data", return_value=Response.ok(None)
        ).start()

        # Act
        delete_all_response = await self.http_client.delete_all_session_data()

        # Assert
        self.assertTrue(delete_all_response.is_success)
        patched_delete_all_method.assert_called_once_with()

    async def test_get_session_data(self) -> None:
        # Arrange
        session_id = uuid4().hex
        session_data = self.faker.paragraph()
        patched_get_method = patch.object(
            self.gateway,
            "get_session_data",
            return_value=Response.ok(session_data),
        ).start()

        # Act
        get_response = await self.http_client.get_session_data(session_id)

        # Assert
        self.assertTrue(get_response.is_success)
        self.assertEqual(get_response.payload, session_data)
        patched_get_method.assert_called_once_with(session_id)
