import sys
import uuid

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
from sbilifeco.gateways.file_read_update import FileReadUpdateGateway


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()
        self.path = f".local/{self.faker.word()}.txt"

        if self.test_type == "unit":
            self.service = FileReadUpdateGateway()
            await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        patch.stopall()
        unlink(self.path)

    async def test_update_and_read(self) -> None:
        # Arrange
        path_id = uuid4().hex
        path_map = {path_id: self.path}
        self.service.set_path_map(path_map)

        content = self.faker.text()

        with open(self.path, "w") as f:
            f.write("")

        # Act
        update_response = await self.service.update(path_id, content.encode("utf-8"))

        # Assert
        self.assertTrue(update_response.is_success, update_response.message)
        with open(self.path, "r") as f:
            file_content = f.read()
        self.assertEqual(file_content, content)

        # Act
        read_response = await self.service.read(path_id)

        # Assert
        self.assertTrue(read_response.is_success, read_response.message)
        assert read_response.payload is not None
        self.assertEqual(read_response.payload.decode("utf-8"), content)
