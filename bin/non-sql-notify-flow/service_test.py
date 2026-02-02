import sys

sys.path.append("./src")

from os import getenv
from asyncio import sleep, gather, timeout
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
from service import NonSQLNotifyMicroservice
from sbilifeco.cp.common.kafka.producer import PubsubProducer
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from sbilifeco.cp.non_sql_notify_flow.paths import Paths


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
        query_flow_port = int(getenv(EnvVars.query_flow_port, Defaults.query_flow_port))

        # Initialise the service(s) here
        self.faker = Faker()

        self.query_flow = QueryFlowHttpClient()
        self.query_flow.set_proto("http").set_host("localhost").set_port(
            query_flow_port
        )

        if self.test_type == "unit":
            self.service = NonSQLNotifyMicroservice()

        # Initialise the client(s) here
        self.producer = PubsubProducer()
        (self.producer.add_host(kafka_url))
        await self.producer.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.producer.async_shutdown()
            await self.service.stop()
        patch.stopall()

    async def __run_awhile(self) -> None:
        try:
            async with timeout(5):
                await self.service.run()
        except TimeoutError:
            pass

    async def __produce(self):
        await sleep(2)
        await self.producer.publish(Paths.BASE.replace("/", ".")[1:], "1")

    async def test_fetch_and_notify(self) -> None:
        # Arrange
        db_id = "nb"
        session_id = uuid4().hex
        question = "What is the meaning of life, the universe and everything?"
        await self.query_flow.query(
            db_id,
            session_id,
            question,
        )

        coros = [self.__produce()]
        if self.test_type == "unit":
            coros.append(self.__run_awhile())

        # Act
        await gather(*coros)

        # Assert
        ...
