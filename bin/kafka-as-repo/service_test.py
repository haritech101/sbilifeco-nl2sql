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
from service import KafkaAsRepoMicroservice
from sbilifeco.cp.query_flow.kafka_producer import QueryFlowEventProducer
from sbilifeco.cp.non_sql_answer_repo.http_client import NonSQLAnswerRepoHttpClient
from sbilifeco.boundaries.query_flow import NonSqlAnswer, GetNonSqlAnswersRequest


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = KafkaAsRepoMicroservice()
            await self.service.run()

        # Initialise the client(s) here
        self.http_client = NonSQLAnswerRepoHttpClient()
        (
            self.http_client.set_proto("http")
            .set_host(staging_host if self.test_type == "staging" else "localhost")
            .set_port(http_port)
        )

        self.kafka_producer = QueryFlowEventProducer()
        (self.kafka_producer.add_host(kafka_url))
        await self.kafka_producer.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        await self.kafka_producer.async_shutdown()
        patch.stopall()

    async def test_get_non_sql_answers(self) -> None:
        # Arrange
        answers = [
            NonSqlAnswer(
                session_id=uuid4().hex,
                db_id=uuid4().hex,
                question=self.faker.sentence(),
                answer=self.faker.paragraph(),
            )
            for _ in range(randint(2, 5))
        ]
        for answer in answers:
            await self.kafka_producer.on_no_sql(answer)

        # Act
        response = await self.http_client.get_non_sql_answers(GetNonSqlAnswersRequest())

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)
        self.assertEqual(answers, response.payload)
