from json import load
from unittest import IsolatedAsyncioTestCase
from service import MetadataStorageMicroservice
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from os import getenv
from envvars import EnvVars, Defaults
from dotenv import load_dotenv


class ServiceTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.microservice_port, Defaults.microservice_port))

        if self.test_type == "unit":
            self.service = MetadataStorageMicroservice()
            await self.service.start()

        self.client = MetadataStorageHttpClient()
        self.client.set_port(http_port).set_proto("http").set_host("localhost")

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
