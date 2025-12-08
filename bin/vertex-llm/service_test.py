import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from service import VertexLLMMicroservice
from sbilifeco.cp.llm.http_client import LLMHttpClient


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        if self.test_type == "unit":
            http_port = int(
                getenv(EnvVars.http_port_unittest, Defaults.http_port_unittest)
            )
        else:
            http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        if self.test_type == "unit":
            self.service = VertexLLMMicroservice()
            await self.service.start()

        # Initialise the client(s) here
        self.client = LLMHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(http_port)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # await self.service.async_shutdown()
        ...

    async def test(self) -> None:
        # Arrange
        question = "What is the meaning of life, the universe, and everything?"

        # Act
        response = await self.client.generate_reply(question)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        self.assertIn("42", response.payload)
