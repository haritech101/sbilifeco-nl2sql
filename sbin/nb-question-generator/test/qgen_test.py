import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from sbin.envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbin.qgen import QGen
from pprint import pprint


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        db_id = getenv(EnvVars.db_id, "")
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))
        llm_template_file = getenv(
            EnvVars.llm_template_file, Defaults.llm_template_file
        )
        metadata_storage_proto = getenv(
            EnvVars.metadata_storage_proto, Defaults.metadata_storage_proto
        )
        metadata_storage_host = getenv(
            EnvVars.metadata_storage_host, Defaults.metadata_storage_host
        )
        metadata_storage_port = int(
            getenv(EnvVars.metadata_storage_port, Defaults.metadata_storage_port)
        )

        # Initialise the service(s) here
        self.service = (
            QGen()
            .set_llm_details(llm_proto, llm_host, llm_port, llm_template_file)
            .set_metadata_storage_details(
                metadata_storage_proto,
                metadata_storage_host,
                metadata_storage_port,
                db_id,
            )
        )

        await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()

    async def test_generate(self) -> None:
        # Arrange

        # Act
        response = await self.service.generate()

        # Assert
        assert response is not None

        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        self.assertTrue(response.payload)
        pprint(response.payload)
