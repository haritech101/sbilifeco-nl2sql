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
from sbilifeco.boundaries.query_flow import INonSqlAnswerRepo, GetNonSqlAnswersRequest
from sbilifeco.cp.non_sql_answer_repo.http_server import NonSQLAnswerRepoHTTPServer
from sbilifeco.cp.non_sql_answer_repo.http_client import NonSQLAnswerRepoHttpClient
from sbilifeco.boundaries.query_flow import NonSqlAnswer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        self.repo = AsyncMock(INonSqlAnswerRepo)

        if self.test_type == "unit":
            self.service = NonSQLAnswerRepoHTTPServer().set_repo(self.repo)
            self.service.set_http_port(http_port)
            await self.service.listen()

        # Initialise the client(s) here
        self.client = NonSQLAnswerRepoHttpClient()
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

    async def test_get_non_sql_answers(self) -> None:
        # Arrange
        answers = [
            NonSqlAnswer(
                db_id=str(uuid4()),
                session_id=str(uuid4()),
                question=self.faker.sentence(),
                answer=self.faker.paragraph(),
            )
            for _ in range(randint(2, 5))
        ]

        patch.object(
            self.repo,
            "get_non_sql_answers",
            AsyncMock(return_value=Response.ok(answers)),
        ).start()

        # Act
        response = await self.client.get_non_sql_answers(GetNonSqlAnswersRequest())

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)
        self.assertEqual(response.payload, answers)
