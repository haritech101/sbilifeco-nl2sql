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
from sbilifeco.cp.non_sql_notify_flow.kafka_consumer import NonSqlNotifyTriggerConsumer
from sbilifeco.cp.common.kafka.producer import PubsubProducer
from sbilifeco.boundaries.non_sql_notify_flow import AbstractNonSqlNotifyFlow
from sbilifeco.cp.non_sql_notify_flow.paths import Paths


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
        max_items = int(getenv(EnvVars.max_items, Defaults.max_items))

        # Initialise the service(s) here
        self.faker = Faker()

        self.flow = AsyncMock(AbstractNonSqlNotifyFlow)

        if self.test_type == "unit":
            self.consumer = NonSqlNotifyTriggerConsumer()
            self.consumer.set_flow(self.flow).add_host(kafka_url)
            await self.consumer.async_init()

        # Initialise the client(s) here
        self.producer = PubsubProducer()
        (self.producer.add_host(kafka_url))
        await self.producer.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.producer.async_shutdown()
            await self.consumer.async_shutdown()
        patch.stopall()

    async def test_consume_once(self) -> None:
        # Arrange
        fn_flow = patch.object(
            self.flow, "fetch_and_notify", AsyncMock(return_value=None)
        ).start()

        # Act
        await gather(
            self.consumer.consume(timeout=5),
            self.producer.publish(Paths.BASE.replace("/", ".")[1:], "1"),
        )

        # Assert
        fn_flow.assert_called_once()

    async def __listen_and_stop(self) -> None:
        try:
            async with timeout(5):
                await self.consumer.listen()
        except TimeoutError:
            pass

    async def test_consume_forever(self) -> None:
        # Arrange
        fn_flow = patch.object(
            self.flow, "fetch_and_notify", AsyncMock(return_value=None)
        ).start()

        # Act
        await gather(
            self.__listen_and_stop(),
            self.producer.publish(Paths.BASE.replace("/", ".")[1:], "1"),
        )

        # Assert
        fn_flow.assert_called_once()
