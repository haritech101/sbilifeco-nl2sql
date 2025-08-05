import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from faker import Faker

# Import the necessary service(s) here
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
