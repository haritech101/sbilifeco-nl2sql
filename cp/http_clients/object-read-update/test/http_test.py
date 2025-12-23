import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from sbilifeco.models.base import Response
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbilifeco.boundaries.object_read_update import IObjectReadUpdate
from sbilifeco.cp.object_read_update.http_client import ObjectReadUpdateHttpClient
from sbilifeco.cp.object_read_update.http_server import ObjectReadUpdateHttpServer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.service = AsyncMock(spec=IObjectReadUpdate)

        self.http_server = (
            ObjectReadUpdateHttpServer()
            .set_object_read_update(self.service)
            .set_http_port(http_port)
        )
        await self.http_server.listen()

        # Initialise the client(s) here
        self.http_client = ObjectReadUpdateHttpClient()
        (self.http_client.set_proto("http").set_host("localhost").set_port(http_port))

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.http_server.stop()
        patch.stopall()

    async def test_read(self) -> None:
        # Arrange
        content = self.faker.word().encode("utf-8")
        fn_read = patch.object(
            self.service, "read", AsyncMock(return_value=Response.ok(content))
        ).start()
        object_id = uuid4().hex

        # Act
        response = await self.http_client.read(object_id)

        # Assert
        fn_read.assert_called_once_with(object_id)
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertEqual(response.payload, content)

    async def test_update(self) -> None:
        # Arrange
        fn_update = patch.object(
            self.service, "update", AsyncMock(return_value=Response.ok(None))
        ).start()
        object_id = uuid4().hex
        content = self.faker.word().encode("utf-8")

        # Act
        response = await self.http_client.update(object_id, content)

        # Assert
        fn_update.assert_called_once_with(object_id, content)
        self.assertTrue(response.is_success, response.message)
