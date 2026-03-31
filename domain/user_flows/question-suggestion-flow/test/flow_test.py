import sys

sys.path.append("./src")

from json import dumps
from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from dotenv import load_dotenv
from envvars import EnvVars
from faker import Faker

# Import the necessary service(s) here
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.question_suggestion_flow import (
    QuestionSuggestionRequest,
)
from sbilifeco.flows.question_suggestion_flow import QuestionSuggestionFlow
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, Field, Table


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        prompt_file = getenv(EnvVars.prompt_file, "")

        # Initialise the service(s) here
        self.faker = Faker()

        self.metadata_storage: IMetadataStorage = AsyncMock(spec=IMetadataStorage)
        self.llm: ILLM = AsyncMock(spec=ILLM)

        self.service = (
            QuestionSuggestionFlow()
            .set_metadata_storage(self.metadata_storage)
            .set_llm(self.llm)
            .set_prompt_file(prompt_file)
        )
        await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        patch.stopall()

    async def test_suggest(self) -> None:
        # Arrange
        request = QuestionSuggestionRequest(db_id="nb")
        db_metadata = DB(
            id=request.db_id,
            name=self.faker.word(),
            description=self.faker.sentence(),
            tables=[
                Table(
                    id=self.faker.word(),
                    name=self.faker.word(),
                    description=self.faker.sentence(),
                    fields=[
                        Field(
                            id=self.faker.word(),
                            type="VARCHAR",
                            name=self.faker.word(),
                            description=self.faker.sentence(),
                        )
                    ],
                )
            ],
        )
        suggested_questions = [
            self.faker.sentence() for _ in range(request.num_suggestions_per_batch)
        ]

        fn_get_db = patch.object(
            self.metadata_storage,
            "get_db",
            AsyncMock(return_value=Response.ok(db_metadata)),
        ).start()
        fn_llm_reply = patch.object(
            self.llm,
            "generate_reply",
            AsyncMock(
                return_value=Response.ok(
                    f'```json\n{{"questions": {dumps(suggested_questions)}}}\n```'
                )
            ),
        ).start()

        # Act
        response = await self.service.suggest(request)

        # Assert
        # Was the call successful?
        self.assertTrue(response.is_success, response.message)

        # Was a stream returned?
        stream = response.payload
        assert stream is not None
        self.assertTrue(stream)

        # Was DB metadata fetched for the correct DB?
        fn_get_db.assert_called_once_with(
            request.db_id,
            with_tables=True,
            with_fields=True,
        )

        next_question = await anext(stream, None)

        # Was LLM called to generate question suggestions based on the DB metadata?
        fn_llm_reply.assert_called_once()
        context = fn_llm_reply.call_args.args[0]
        self.assertIn(db_metadata.name, context)

        assert db_metadata.tables is not None
        self.assertIn(db_metadata.tables[0].name, context)

        assert db_metadata.tables[0].fields is not None
        self.assertIn(db_metadata.tables[0].fields[0].name, context)

        # At least one question should be suggested in the stream
        self.assertIsNotNone(
            next_question, "Expected at least one suggested question in the stream"
        )

        num_reps = 3
        async for suggested_question in stream:
            self.assertTrue(suggested_question)
            num_reps -= 1
            if num_reps == 0:
                break
