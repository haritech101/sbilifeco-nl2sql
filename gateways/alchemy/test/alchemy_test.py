import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbilifeco.gateways.alchemy import Alchemy


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)

        connection_string = getenv(
            EnvVars.connection_string, Defaults.connection_string
        )

        # Initialise the service(s) here
        self.alchemy = Alchemy()
        self.alchemy.set_connection_string(connection_string)
        await self.alchemy.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.alchemy.async_shutdown()

    async def test_execute(self) -> None:
        # Arrange
        sql = "select 1 as number"

        # Act
        response = await self.alchemy.execute_query(sql)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        row = next(iter(response.payload))
        assert row is not None
        self.assertEqual(row.get("number"), 1)
