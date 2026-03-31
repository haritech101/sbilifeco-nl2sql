import sys

sys.path.append("./src")

from os import getenv
from asyncio import sleep, gather
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from pprint import pprint, pformat
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from service import QuestionSuggestionMicroservice
from sbilifeco.cp.question_suggestion_flow.http_client import (
    QuestionSuggestionHttpClient,
)
from sbilifeco.boundaries.question_suggestion_flow import QuestionSuggestionRequest


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.db_id = getenv(EnvVars.db_id, "")

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = QuestionSuggestionMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.client = QuestionSuggestionHttpClient()
        (
            self.client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port)
        )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.stop()
        patch.stopall()

    async def test_suggest(self) -> None:
        # Arrange
        req = QuestionSuggestionRequest(db_id=self.db_id)

        # Act
        suggestion_response = await self.client.suggest(req)

        # Assert
        self.assertTrue(suggestion_response.is_success, suggestion_response.message)

        stream = suggestion_response.payload
        assert stream is not None
        self.assertTrue(stream)

        suggestions = await anext(stream, None)
        assert suggestions is not None
        for suggestion in suggestions:
            self.assertTrue(suggestion.question)
            print(suggestion.question)
