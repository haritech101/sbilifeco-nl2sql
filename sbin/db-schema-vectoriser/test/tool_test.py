from curses import meta
import sys

sys.path.append("./src")

from os import getenv
from asyncio import sleep, gather
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Base, patch
from dotenv import load_dotenv
from sbilifeco.sbin.envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint, random
from faker import Faker
from datetime import datetime, date
from pprint import pprint, pformat
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, Table, Field

# Import the necessary service(s) here
from sbilifeco.sbin.db_schema_vectoriser import DbSchemaVectoriser
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.boundaries.vector_repo import BaseVectorRepo


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        self.metadata_storage: IMetadataStorage = AsyncMock(spec=IMetadataStorage)
        self.vectoriser = BaseVectoriser()
        self.vector_repo = BaseVectorRepo()

        self.service = (
            DbSchemaVectoriser()
            .set_metadata_storage(self.metadata_storage)
            .set_vectoriser(self.vectoriser)
            .set_vector_repo(self.vector_repo)
        )
        await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        patch.stopall()

    async def test_vectorise(self) -> None:
        # Arrange
        schema = self.faker.word()
        metadata = DB(
            id=self.faker.word(),
            name=self.faker.word(),
            description=self.faker.sentence(),
            tables=[
                Table(
                    id=self.faker.word(),
                    name=self.faker.word(),
                    description=self.faker.sentence(),
                    fields=[
                        Field(
                            id=self.faker.word(),
                            name=self.faker.word(),
                            type=self.faker.word(),
                            description=self.faker.sentence(),
                        )
                        for _ in range(3)
                    ],
                )
                for _ in range(3)
            ],
        )
        num_elements = 0
        if metadata.tables:
            for table in metadata.tables:
                num_elements += 1  # For the table itself
                if table.fields:
                    num_elements += len(table.fields)  # For the fields in the table

        fn_get_db = patch.object(
            self.metadata_storage, "get_db", return_value=Response.ok(metadata)
        ).start()

        fn_vectorise = patch.object(
            self.vectoriser,
            "vectorise",
            return_value=Response.ok([random() for _ in range(16)]),
        ).start()

        fn_crupdate = patch.object(
            self.vector_repo, "crupdate", return_value=Response.ok(None)
        ).start()

        # Act
        await self.service.vectorise(schema)

        # Assert
        # Is DB metadata fetched from metadata storage?
        fn_get_db.assert_called_once()
        self.assertEqual(fn_get_db.call_args.kwargs.get("db_id", ""), schema)

        # Are the correct number of elements vectorised?
        self.assertEqual(fn_vectorise.call_count, num_elements)

        # Are the correct number of elements upserted to the vector repo?
        self.assertEqual(fn_crupdate.call_count, num_elements)
