import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from sbilifeco.models.base import Response
from pprint import pprint

# Import the necessary service(s) here
from asyncio import gather, sleep
from sbilifeco.boundaries.query_flow import NonSqlAnswer
from sbilifeco.cp.query_flow_listener.kafka_producer import QueryFlowEventKafkaProducer
from sbilifeco.cp.common.kafka.consumer import PubsubConsumer
from sbilifeco.cp.query_flow.paths import Paths


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
        self.topic_non_sql = Paths.NON_SQLS.replace("/", ".")[1:]
        self.topic_failures = Paths.FAILURES.replace("/", ".")[1:]

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = QueryFlowEventKafkaProducer()
            self.service.add_host(kafka_url)
            await self.service.async_init()

        # Initialise the client(s) here
        self.client = PubsubConsumer().add_host(kafka_url)
        self.client.add_subscription(self.topic_non_sql)
        await self.client.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        patch.stopall()

    async def test_non_sql(self) -> None:
        # Arrange
        non_sql_answer = NonSqlAnswer(
            session_id=str(uuid4()),
            db_id=str(uuid4()),
            question=self.faker.sentence(),
            answer=self.faker.paragraph(),
        )

        # Act
        gathered = await gather(self.__produce(non_sql_answer), self.__consume())

        # Assert
        response = gathered[1]
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        self.assertTrue(response.payload)

        fetched_answer = NonSqlAnswer.model_validate_json(response.payload)
        pprint(non_sql_answer)
        pprint(fetched_answer)
        self.assertEqual(non_sql_answer, fetched_answer)

    async def __consume(self) -> Response[str]:
        print("Starting to consume in test case", flush=True)
        attempts = 3
        payload = None
        print(
            f"Attempting consumption {attempts} times on topic {self.topic_non_sql}",
            flush=True,
        )
        source = self.client.consume_forever(interval=2.0)
        async for response in source:
            payload = response.payload
            if payload is not None:
                return response

            attempts -= 1
            print(f"No payload received, attempts left: {attempts}")
            if attempts == 0:
                break

        return Response.ok(None)

    async def __produce(self, non_sql_answer: NonSqlAnswer) -> None:
        # await sleep(0.5)
        await self.service.on_no_sql(non_sql_answer)
