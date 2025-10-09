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
from sbin.http import QGenHttpClient, QGenHttpServer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".env.test")

        conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))
        http_listen_port = int(
            getenv(EnvVars.http_listen_port, Defaults.http_listen_port)
        )
        self.test_mode = getenv("TEST_MODE", "unit").lower()

        if self.test_mode == "unit":
            # Initialise the service(s) here
            self.service = (
                QGen()
                .set_conn_string(conn_string)
                .set_llm_scheme(llm_proto, llm_host, llm_port)
            )
            await self.service.async_init()

            self.http_server = QGenHttpServer().set_qgen(self.service)
            self.http_server.set_http_port(http_listen_port)
            await self.http_server.listen()

        # Initialise the client(s) here
        self.http_client = QGenHttpClient()
        self.http_client.set_proto("http").set_host("localhost").set_port(
            http_listen_port
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_mode == "unit":
            await self.http_server.stop()
            await self.service.async_shutdown()

    async def test_generate_with_llm(self) -> None:
        if self.test_mode != "unit":
            self.skipTest("Skipping unit test in non-unit mode")

        # Arrange
        num_tests = -1

        # Act
        result = await self.service.generate_with_llm(num_tests)

        # Assert
        print(result)
        assert result is not None

    async def test_generate_using_http(self) -> None:
        # Arrange
        num_tests = -1

        # Act
        response = await self.http_client.generate_requests(num_tests)

        # Assert
        print(response)

        self.assertTrue(response.is_success, response.message)

        assert response.payload is not None
        self.assertTrue(response.payload)
