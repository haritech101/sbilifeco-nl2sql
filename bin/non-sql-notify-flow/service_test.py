import sys

sys.path.append("./src")

from os import getenv, unlink
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
from playwright.async_api import async_playwright
from pathlib import Path


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
        query_flow_port = int(getenv(EnvVars.query_flow_port, Defaults.query_flow_port))
        self.web_page_path = getenv(EnvVars.web_page_path, Defaults.web_page_path)
        template_path = getenv(EnvVars.template_path, Defaults.template_path)

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

        self.playwright = await async_playwright().start()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        unlink(self.web_page_path)
        await self.page.close()
        await self.browser.close()
        await self.playwright.stop()
        await self.producer.async_shutdown()
        if self.test_type == "unit":
            await self.service.stop()
        patch.stopall()

    async def __run_awhile(self) -> None:
        try:
            async with timeout(7):
                await self.service.run()
        except TimeoutError:
            pass

    async def __produce(self):
        await sleep(3)
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
        await sleep(3)
        abs_path_to_report = Path(self.web_page_path).resolve()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.goto(f"file://{abs_path_to_report}")
        content = await self.page.content()
        self.assertIn(db_id, content)
        self.assertIn(question, content)
