from unittest import IsolatedAsyncioTestCase
from os import getenv
from dotenv import load_dotenv
from service import LLMExecutable
from sbilifeco.cp.llm.http_client import LLMHttpClient
from envvars import EnvVars, Defaults
from requests import Request


class ServiceTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        service_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        self.service = LLMExecutable()
        await self.service.start()

        self.client = LLMHttpClient()
        self.client.set_proto("http")
        self.client.set_host("localhost")
        self.client.set_port(service_port)

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_request(self) -> None:
        # Arrange
        question = "Which letter comes after 'iks' in the German alphabet?"

        # Act
        llm_response = await self.client.generate_sql(question)

        # Assert
        self.assertTrue(llm_response.is_success, llm_response.message)
        assert llm_response.payload is not None
