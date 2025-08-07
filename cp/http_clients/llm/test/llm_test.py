import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from faker import Faker
from sbilifeco.models.base import Response
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.cp.llm.microservice import LLMMicroservice
from sbilifeco.cp.llm.http_client import LLMHttpClient


class LLMTest(IsolatedAsyncioTestCase):
    HTTP_PORT = 8181

    async def asyncSetUp(self) -> None:
        self.llm: ILLM = AsyncMock(spec=ILLM)

        self.microservice = LLMMicroservice()
        self.microservice.set_llm(self.llm).set_http_port(self.HTTP_PORT)

        await self.microservice.listen()

        self.client = LLMHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(self.HTTP_PORT)

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        await self.microservice.stop()
        return await super().asyncTearDown()

    async def test_sequence(self) -> None:
        # Arrange
        question = self.faker.sentence()
        reply = self.faker.paragraph()
        patched_generate_reply = patch.object(
            self.llm, "generate_reply", return_value=Response.ok(reply)
        ).start()

        # Act
        response = await self.client.generate_reply(question)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        patched_generate_reply.assert_called_once_with(question)
