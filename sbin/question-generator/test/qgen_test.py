import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from pprint import pprint
from sbin.envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbin.qgen import (
    QGen,
    QGenRequest,
    QGenMetric,
    QGenRegion,
    QGenProduct,
    QGenTimeframe,
)


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".env.test")

        conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

        # Initialise the service(s) here
        self.service = (
            QGen()
            .set_conn_string(conn_string)
            .set_llm_scheme(llm_proto, llm_host, llm_port)
        )
        await self.service.async_init()

        # Initialise the client(s) here
        ...

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        ...

    async def test_generate_with_llm(self) -> None:
        # Arrange
        num_tests = -1

        # Act
        result = await self.service.generate_with_llm(num_tests)

        # Assert
        print(result)
        assert result is not None
