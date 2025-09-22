from unittest import IsolatedAsyncioTestCase
from os import getenv
from dotenv import load_dotenv
from service import LLMMicroservice
from sbilifeco.cp.llm.http_client import LLMHttpClient
from envvars import EnvVars, Defaults
from pprint import pprint


class ServiceTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        test_type = getenv("TEST_TYPE", "unit")
        service_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        if test_type == "unit":
            self.service = LLMMicroservice()
            await self.service.start()

        self.client = LLMHttpClient()
        self.client.set_proto("http")
        self.client.set_host("tech101.in" if test_type == "staging" else "localhost")
        self.client.set_port(service_port)

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_request(self) -> None:
        # Arrange
        question = "Which letter comes after 'iks' in the German alphabet?"

        # Act
        llm_response = await self.client.generate_reply(question)

        # Assert
        self.assertTrue(llm_response.is_success, llm_response.message)
        pprint(llm_response.payload)
        assert llm_response.payload is not None
