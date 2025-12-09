import datetime
from random import randint
import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from faker import Faker

# Import the necessary service(s) here
from datetime import date, datetime
from sbilifeco.gateways.redis import Redis


class RedisTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        # Initialize the service(s) here
        redis_host = getenv(EnvVars.redis_host, Defaults.redis_host)
        redis_port = int(getenv(EnvVars.redis_port, Defaults.redis_port))
        redis_db = int(getenv(EnvVars.redis_db, Defaults.redis_db))

        self.service = (
            Redis()
            .set_redis_host(redis_host)
            .set_redis_port(redis_port)
            .set_redis_db(redis_db)
        )
        await self.service.async_init()

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()

    async def test_create(self) -> None:
        # Arrange
        key = "person_name"
        value = self.faker.name()

        # Act
        create_response = await self.service.update_session_data(key, value)

        # Assert
        self.assertTrue(create_response.is_success, create_response.message)

        fetch_response = await self.service.get_session_data(key)
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        self.assertEqual(fetch_response.payload, value)

    async def test_update(self) -> None:
        # Arrange
        key = "person_name"
        old_value = self.faker.name()
        new_value = self.faker.name()
        await self.service.update_session_data(key, old_value)

        # Act
        update_response = await self.service.update_session_data(key, new_value)

        # Assert
        self.assertTrue(update_response.is_success, update_response.message)

        fetch_response = await self.service.get_session_data(key)
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        self.assertEqual(fetch_response.payload, new_value)

    async def test_delete(self) -> None:
        # Arrange
        key = "person_name"
        value = self.faker.name()
        await self.service.update_session_data(key, value)

        # Act
        delete_response = await self.service.delete_session_data(key)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)

        fetch_response = await self.service.get_session_data(key)
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        self.assertEqual(fetch_response.payload, "")

    async def test_delete_all(self) -> None:
        # Arrange
        key1 = "person_name1"
        value1 = self.faker.name()
        key2 = "person_name2"
        value2 = self.faker.name()
        await self.service.update_session_data(key1, value1)
        await self.service.update_session_data(key2, value2)

        # Act
        delete_all_response = await self.service.delete_all_session_data()

        # Assert
        self.assertTrue(delete_all_response.is_success, delete_all_response.message)

        fetch_response1 = await self.service.get_session_data(key1)
        fetch_response2 = await self.service.get_session_data(key2)
        self.assertEqual(fetch_response1.payload, "")
        self.assertEqual(fetch_response2.payload, "")

    async def test_count_by_named_division(self) -> None:
        # Arrange
        key = self.faker.word()
        division = self.faker.word()
        num_entries = randint(1, 1000)

        await self.service.update_session_data(f"{key}::{division}", str(num_entries))

        # Act
        count_response = await self.service.count_by_named_division(key, division)

        # Assert
        self.assertTrue(count_response.is_success, count_response.message)
        assert count_response.payload is not None
        self.assertEqual(count_response.payload, num_entries)

    async def test_count_by_numeric_range(self) -> None:
        # Arrange
        key = self.faker.word()
        min = randint(1, 5) * 100
        max = randint(6, 10) * 100
        num_entries = randint(1000, 2000)

        await self.service.update_session_data(f"{key}::{min}::{max}", str(num_entries))

        # Act
        count_response = await self.service.count_by_numeric_range(key, min, max)

        # Assert
        self.assertTrue(count_response.is_success, count_response.message)
        assert count_response.payload is not None
        self.assertEqual(count_response.payload, num_entries)

    async def test_count_by_date_range(self) -> None:
        # Arrange
        key = self.faker.word()
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        num_entries = randint(1000, 2000)

        await self.service.update_session_data(
            f"{key}::{start_date}::{end_date}", str(num_entries)
        )

        # Act
        count_response = await self.service.count_by_date_range(
            key, start_date, end_date
        )

        # Assert
        self.assertTrue(count_response.is_success, count_response.message)
        assert count_response.payload is not None
        self.assertEqual(count_response.payload, num_entries)

    async def test_count_by_boolean(self) -> None:
        # Arrange
        key = self.faker.word()
        bool_value = randint(0, 1) == 1
        num_entries = randint(1, 1000)

        await self.service.update_session_data(f"{key}::{bool_value}", str(num_entries))

        # Act
        count_response = await self.service.count_by_boolean(key, bool_value)

        # Assert
        self.assertTrue(count_response.is_success, count_response.message)
        assert count_response.payload is not None
        self.assertEqual(count_response.payload, num_entries)
