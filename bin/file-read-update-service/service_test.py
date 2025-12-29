import sys

sys.path.append("./src")

from os import getenv, unlink
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
from service import FileReadUpdateService
from sbilifeco.cp.object_read_update.http_client import ObjectReadUpdateHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = FileReadUpdateService()
            await self.service.run()

        # Initialise the client(s) here
        self.client = ObjectReadUpdateHttpClient()
        (
            self.client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        patch.stopall()
        try:
            unlink("./.local/.test.md")
        except Exception:
            ...

    async def test_update_and_read(self) -> None:
        # Arrange
        object_id = "test"
        file_path = "./.local/.test.md"
        content = self.faker.paragraph()

        # Act
        update_response = await self.client.update(object_id, content.encode("utf-8"))

        # Assert
        self.assertTrue(update_response.is_success, update_response.message)
        if self.test_type == "unit":
            with open(file_path, "r") as f:
                file_content = f.read()
            self.assertEqual(file_content, content)

        # Act
        read_response = await self.client.read(object_id)
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None
        self.assertEqual(read_response.payload.decode("utf-8"), content)
