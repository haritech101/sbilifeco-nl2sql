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
from sbilifeco.boundaries.question_suggestion_flow import (
    IQuestionSuggestionFlow,
    QuestionSuggestionRequest,
    SuggestedQuestion,
)
from sbilifeco.cp.question_suggestion_flow.http_server import (
    QuestionSuggestionHttpServer,
)
from sbilifeco.cp.question_suggestion_flow.http_client import (
    QuestionSuggestionHttpClient,
)


class QuestionSuggestionHttpTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.flow: IQuestionSuggestionFlow = AsyncMock(spec=IQuestionSuggestionFlow)

        self.service = (
            QuestionSuggestionHttpServer()
            .set_question_suggestion_flow(self.flow)
            .set_http_port(http_port)
        )
        await self.service.listen()

        # Initialise the client(s) here
        self.client = QuestionSuggestionHttpClient()
        (self.client.set_proto("http").set_host("localhost").set_port(http_port))

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.stop()
        patch.stopall()

    async def test_suggest(self) -> None:
        # Arrange

        db_id = self.faker.word()
        req = QuestionSuggestionRequest(db_id=db_id)
        suggestion = SuggestedQuestion(question=self.faker.sentence())

        async def __suggest():
            yield [suggestion]

        fn_suggest = patch.object(
            self.flow,
            "suggest",
            return_value=Response.ok(__suggest()),
        ).start()

        # Act
        suggestion_response = await self.client.suggest(req)

        # Assert
        # Is the call successful?
        self.assertTrue(suggestion_response.is_success, suggestion_response.message)

        # Was the flow called?
        fn_suggest.assert_awaited_once_with(req)

        stream = suggestion_response.payload
        assert stream is not None
        self.assertTrue(stream)

        suggestions = await anext(stream, None)
        assert suggestions is not None
        for suggestion in suggestions:
            self.assertTrue(suggestion.question)
