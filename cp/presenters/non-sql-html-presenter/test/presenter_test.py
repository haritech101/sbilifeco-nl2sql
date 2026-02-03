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
from sbilifeco.cp.non_sql_presenter.html_page import NonSqlHtmlPresenter
from sbilifeco.boundaries.query_flow import NonSqlAnswer
from playwright.async_api import async_playwright
from pathlib import Path


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.web_page_path = getenv(EnvVars.web_page_path, Defaults.web_page_path)
        self.template_path = getenv(EnvVars.template_path, Defaults.template_path)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.presenter = (
                NonSqlHtmlPresenter()
                .set_web_page_path(self.web_page_path)
                .set_template_path(self.template_path)
            )
            await self.presenter.async_init()

        # Initialise the client(s) here
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.presenter.async_shutdown()
            await self.page.close()
            await self.browser.close()
            await self.playwright.stop()
        patch.stopall()

    async def test_present(self) -> None:
        # Arrange
        answers = [
            NonSqlAnswer(
                db_id=self.faker.vin(),
                session_id=uuid4().hex,
                question=self.faker.sentence(),
                answer=self.faker.paragraph(),
            )
            for _ in range(3)
        ]
        abs_path = Path(self.web_page_path).absolute()

        # Act
        await self.presenter.present(answers)

        # Assert
        await self.page.goto(f"file://{abs_path}")
        content = await self.page.content()
        for answer in answers:
            self.assertIn(answer.db_id, content)
            self.assertIn(answer.question, content)
            self.assertIn(answer.answer, content)
