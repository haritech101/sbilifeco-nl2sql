import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from sbilifeco.gateways.synmetrix import Synmetrix
from dotenv import load_dotenv
from os import getenv


class SynmetrixTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        load_dotenv()

        db_username = getenv("DB_USERNAME", "")
        db_password = getenv("DB_PASSWORD", "")
        db_host = getenv("DB_HOST", "localhost")
        db_port = int(getenv("DB_PORT", 5432))
        db_name = getenv("DB_NAME", "")

        api_proto = getenv("API_PROTO", "http")
        api_host = getenv("API_HOST", "localhost")
        api_port = int(getenv("API_PORT", 8888))
        api_path = getenv("API_PATH", "")
        api_username = getenv("API_USERNAME", "")
        api_password = getenv("API_PASSWORD", "")

        cube_api_proto = getenv("CUBE_API_PROTO", "http")
        cube_api_host = getenv("CUBE_API_HOST", "localhost")
        cube_api_port = int(getenv("CUBE_API_PORT", 4000))

        self.synmetrix = (
            Synmetrix()
            .set_db_username(db_username)
            .set_db_password(db_password)
            .set_db_host(db_host)
            .set_db_port(db_port)
            .set_db_name(db_name)
            .set_api_proto(api_proto)
            .set_api_host(api_host)
            .set_api_port(api_port)
            .set_api_path(api_path)
            .set_api_username(api_username)
            .set_api_password(api_password)
            .set_cube_api_proto(cube_api_proto)
            .set_cube_api_host(cube_api_host)
            .set_cube_api_port(cube_api_port)
        )
        await self.synmetrix.async_init()

    async def asyncTearDown(self):
        # Teardown code here, if needed
        await self.synmetrix.async_shutdown()

    async def test_get_dbs(self) -> None:
        # Arrange
        # Act
        fetch_response = await self.synmetrix.get_dbs()

        # Assert
        self.assertTrue(fetch_response.is_success)
        assert fetch_response.payload is not None
        self.assertTrue(fetch_response.payload)

        for db in fetch_response.payload:
            self.assertTrue(db.id)
            self.assertTrue(db.name)

    async def test_get_db(self) -> None:
        # Arrange
        db_id = "325d08cc-950f-4759-acc3-2d41a8b604fa"

        # Act
        fetch_response = await self.synmetrix.get_db(db_id, True, True, True, True)

        # Assert
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        assert fetch_response.payload is not None
        self.assertTrue(fetch_response.payload)

        self.assertTrue(fetch_response.payload.id)
        self.assertTrue(fetch_response.payload.name)

        assert fetch_response.payload.tables is not None
        self.assertTrue(fetch_response.payload.tables)
        for table in fetch_response.payload.tables:
            self.assertTrue(table.id)
            self.assertTrue(table.name)
            self.assertTrue(table.description)

            assert table.fields is not None
            self.assertTrue(table.fields)
