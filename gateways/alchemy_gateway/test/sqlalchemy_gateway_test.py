import sys

from sqlalchemy import table

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
from sbilifeco.gateways.sqlalchemy_gateway import SQLAlchemyGateway


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        definitions_path = getenv("DEFINITIONS_PATH", ".local/alchemy")

        # Initialise the service(s) here
        self.faker = Faker()

        self.service = SQLAlchemyGateway()
        self.service.set_definitions_path(definitions_path)
        await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        patch.stopall()

    async def test_get_dbs(self) -> None:
        # Act
        response = await self.service.get_dbs()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        dbs = response.payload
        self.assertTrue(dbs)
        db0 = dbs[0]
        self.assertTrue(db0.id)
        self.assertTrue(db0.name)
        self.assertTrue(db0.description)

    async def test_get_tables(self) -> None:
        # Arrange
        db_id = "nb"

        # Act
        response = await self.service.get_tables(db_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        tables = response.payload
        self.assertTrue(tables)
        table0 = tables[0]
        self.assertTrue(table0.id)
        self.assertTrue(table0.name)
        self.assertTrue(table0.description)

    async def test_get_fields(self) -> None:
        # Arrange
        db_id = "nb"
        table_id = "piwc_workflow_det"

        # Act
        response = await self.service.get_fields(db_id, table_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)
        field0 = response.payload[0]
        self.assertTrue(field0.id)
        self.assertTrue(field0.name)
        self.assertTrue(field0.description)
        self.assertTrue(field0.type)
