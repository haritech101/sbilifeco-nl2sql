import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase

from dotenv import load_dotenv
from sbilifeco.gateways.gemini import Gemini
from sbilifeco.models.db_metadata import DB, Table, Field


class GeminiTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        api_key = getenv("API_KEY", "")
        model = getenv("MODEL", "gemini-1.5-flash")

        self.gemini = Gemini().set_api_key(api_key).set_model(model)
        await self.gemini.async_init()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_generate_reply(self):
        # Arrange
        context = "How are United Kingdom and England different?"

        # Act
        response = await self.gemini.generate_reply(context)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Response payload should not be None"
        self.assertGreater(
            len(response.payload), 0, "Response payload should not be empty"
        )
        print(response.payload)
