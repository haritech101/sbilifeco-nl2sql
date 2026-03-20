import sys

sys.path.append("./src")

from os import getenv
from asyncio import sleep, gather
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from sbilifeco.sbin.envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from pprint import pprint, pformat
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.sbin.db_schema_vectoriser_one_shot import DBSchemaVectoriserService
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        vector_repo_proto = getenv(
            EnvVars.vector_repo_proto, Defaults.vector_repo_proto
        )
        vector_repo_host = getenv(EnvVars.vector_repo_host, Defaults.vector_repo_host)
        vector_repo_port = int(
            getenv(EnvVars.vector_repo_port, Defaults.vector_repo_port)
        )
        self.db_id = getenv(EnvVars.db_id, "")

        # Initialise the service(s) here
        self.faker = Faker()

        self.service = DBSchemaVectoriserService()

        self.client = VectorRepoHttpClient()
        (
            self.client.set_host(vector_repo_host)
            .set_proto(vector_repo_proto)
            .set_port(vector_repo_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.client.delete_by_criteria({"source_id": self.db_id})

    async def test_one_shot(self) -> None:
        # Arrange
        ...

        # Act
        await self.service.start()

        # Assert
        repo_response = await self.client.read_by_criteria({"source_id": self.db_id})
        self.assertTrue(repo_response.is_success)

        records = repo_response.payload
        assert records is not None
        self.assertGreater(len(records), 0)
