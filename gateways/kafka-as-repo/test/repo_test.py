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
from sbilifeco.boundaries.query_flow import GetNonSqlAnswersRequest, NonSqlAnswer
from sbilifeco.gateways.kafka_as_repo import KafkaAsRepo
from sbilifeco.cp.query_flow.kafka_producer import QueryFlowEventProducer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
        consumer_name = getenv(EnvVars.consumer_name, Defaults.consumer_name)
        answer_timeout = float(getenv(EnvVars.answer_timeout, Defaults.answer_timeout))

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = (
                KafkaAsRepo()
                .set_kafka_url(kafka_url)
                .set_consumer_name(consumer_name)
                .set_answer_timeout(answer_timeout)
            )
            await self.service.async_init()

        self.producer = QueryFlowEventProducer()
        self.producer.add_host(kafka_url)
        await self.producer.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        patch.stopall()

    async def test_get_non_sql_answers(self) -> None:
        # Arrange
        non_sql_answers = [
            NonSqlAnswer(
                session_id=uuid4().hex,
                db_id=uuid4().hex,
                question=self.faker.sentence(),
                answer=self.faker.paragraph(),
            )
            for _ in range(2, 5)
        ]
        for non_sql_answer in non_sql_answers:
            await self.producer.on_no_sql(non_sql_answer)

        request = GetNonSqlAnswersRequest()

        # Act
        response = await self.service.get_non_sql_answers(request)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)
        self.assertEqual(non_sql_answers, response.payload)
