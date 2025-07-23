from json import load
from unittest import IsolatedAsyncioTestCase
from service import MetadataStorageExecutable
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from os import getenv
from envvars import EnvVars, Defaults
from dotenv import load_dotenv


class ServiceTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.service = MetadataStorageExecutable()

        self.client = MetadataStorageHttpClient()
        (
            self.client.set_port(
                int(getenv(EnvVars.microservice_port, Defaults.microservice_port))
            )
            .set_proto("http")
            .set_host("localhost")
        )

        await self.service.start()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_get_dbs(self):
        dbs_response = await self.client.get_dbs()

        self.assertTrue(dbs_response.is_success, dbs_response.message)
        assert dbs_response.payload, "List of databases should not be empty"

        for db in dbs_response.payload:
            self.assertTrue(db.id, "Database ID should not be empty")
            self.assertTrue(db.name, "Database name should not be empty")
            # self.assertTrue(db.description, "Database description should not be empty")
