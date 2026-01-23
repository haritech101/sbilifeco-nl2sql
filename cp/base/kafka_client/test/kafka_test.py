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
from asyncio import create_task, gather, sleep

# Import the necessary service(s) here
from sbilifeco.cp.common.kafka.producer import PubsubProducer
from sbilifeco.cp.common.kafka.consumer import PubsubConsumer


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)

        # Initialise the service(s) here
        self.faker = Faker()

        self.producer = PubsubProducer()
        (self.producer.add_host(kafka_url))
        await self.producer.async_init()

        # Initialise the client(s) here
        self.consumer = PubsubConsumer()
        (self.consumer.add_host(kafka_url))
        await self.consumer.async_init()

    async def asyncTearDown(self) -> None:
        await self.consumer.async_shutdown()
        await self.producer.async_shutdown()
        patch.stopall()

    async def consume_and_leave(self, expected_content: str) -> None:
        async for consume_response in self.consumer.consume_forever():
            # Assert
            self.assertTrue(consume_response.is_success, consume_response.message)
            if consume_response.payload == expected_content:
                await self.consumer.stop_consuming()
            else:
                break

    async def test_consume_once(self) -> None:
        # Arrange
        topic = self.faker.word()
        content = self.faker.sentence()
        await self.consumer.subscribe(topic)

        # Act
        publish_response = await self.producer.publish(topic, content)

        # Assert
        self.assertTrue(publish_response.is_success, publish_response.message)

        # Act
        consume_response = await self.consumer.consume()

        # Assert
        self.assertTrue(consume_response.is_success, consume_response.message)
        assert consume_response.payload is not None
        self.assertEqual(consume_response.payload, content)

    async def test_consume_forever(self) -> None:
        # Arrange
        topic = self.faker.word()
        content = self.faker.sentence()
        await self.consumer.subscribe(topic)

        task_consume = create_task(self.consume_and_leave(content))
        task_publish = create_task(self.producer.publish(topic, content))

        # Act and assert
        await gather(task_consume, task_publish)
