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
from service import SQLAlchemyGatewayService
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = SQLAlchemyGatewayService()
            await self.service.run()

        # Initialise the client(s) here
        self.client = MetadataStorageHttpClient()
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

    async def test_get_dbs(self) -> None:
        # Arrange
        ...

        # Act
        response = await self.client.get_dbs()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)

    async def test_get_single_db_hierarchy(self) -> None:
        # Arrange
        db_id = "nb"

        # Act
        response = await self.client.get_db(db_id, with_tables=True, with_fields=True)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)

        db = response.payload
        self.assertTrue(db.name)
        self.assertTrue(db.description)
        assert db.tables is not None
        self.assertTrue(db.tables)

        table = db.tables[0]
        self.assertTrue(table.name)
        self.assertTrue(table.description)
        assert table.fields is not None
        self.assertTrue(table.fields)
