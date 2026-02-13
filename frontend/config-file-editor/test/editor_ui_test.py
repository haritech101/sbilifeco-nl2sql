from asyncio import sleep
import sys

sys.path.append("./src")

from os import error, getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint
from faker import Faker
from datetime import datetime, date
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from playwright.async_api import async_playwright, Route, expect


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        self.login_page = getenv(EnvVars.login_page, "")

        # Initialise the service(s) here
        self.faker = Faker()

        self.home_url = f"http://localhost:{self.http_port}/editor-ui/"
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=False, timeout=5000)
        self.page = await self.browser.new_page()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        # if self.test_type == "unit":
        #     await self.service.async_shutdown()
        patch.stopall()
        await self.page.close()
        await self.browser.close()
        await self.pw.stop()

    async def __login(self):
        await self.page.goto(self.home_url)
        await self.page.wait_for_load_state("networkidle")

        username_input = await self.page.wait_for_selector(
            "#input-username", timeout=5000
        )
        assert username_input is not None
        await username_input.fill(getenv("TEST_USERNAME", ""))

        password_input = await self.page.wait_for_selector(
            "#input-password", timeout=5000
        )
        assert password_input is not None
        await password_input.fill(getenv("TEST_PASSWORD", ""))

        submit_button = await self.page.wait_for_selector(
            "#action-submit", timeout=5000
        )
        assert submit_button is not None
        await submit_button.click()

        await self.page.wait_for_load_state("networkidle")
        self.assertIn(self.home_url, self.page.url)

    async def test_that_home_loads_login_page(self):
        await self.page.goto(self.home_url)
        await self.page.wait_for_load_state("networkidle")
        self.assertIn(self.login_page, self.page.url)

    async def test_that_selected_file_loads(self) -> None:
        # Arrange
        file_content = self.faker.paragraph()
        response_to_get_file: Response[str] = Response.ok(file_content)

        async def handle_get_file(route):
            await route.fulfill(
                status=200,
                body=response_to_get_file.model_dump_json(),
                headers={"Content-Type": "application/json"},
            )

        selected_file = "prompt"

        # await self.page.route(
        #     f"**/api/v1/updatable-objects/{selected_file}", handle_get_file
        # )

        await self.__login()

        # Act
        await self.page.select_option("#which-file", selected_file)
        await sleep(1)

        # Assert
        textarea = await self.page.wait_for_selector("#file-content", timeout=5000)
        assert textarea is not None
        textarea_content = await textarea.input_value()
        textarea_content = textarea_content.strip()
        self.assertTrue(textarea_content)
        # self.assertEqual(textarea_content, file_content)

    async def test_that_changes_are_saved(self) -> None:
        # Arrange
        async def handle_to_success(route: Route):
            if route.request.method == "GET":
                await route.continue_()
                return

            response_to_save_file: Response[None] = Response.ok(None)
            await route.fulfill(
                status=200,
                body=response_to_save_file.model_dump_json(),
                headers={"Content-Type": "application/json"},
            )

        new_content = self.faker.paragraph()
        await self.page.route("**/api/v1/updatable-objects/test", handle_to_success)
        await self.page.goto(self.home_url)
        await self.page.select_option("#which-file", "test")
        await sleep(1)

        textarea = await self.page.wait_for_selector("#file-content", timeout=5000)
        assert textarea is not None
        await textarea.fill(new_content)

        # Act
        submit_button = await self.page.wait_for_selector("#save-file", timeout=5000)
        assert submit_button is not None
        await submit_button.click()

        # Assert
        feedback_panel = await self.page.query_selector("#feedback-panel")
        assert feedback_panel is not None
        feedback_message = await feedback_panel.inner_text()
        feedback_message = feedback_message.strip().lower()
        self.assertIn("success", feedback_message)

    async def test_that_changes_lead_to_error(self) -> None:
        # Arrange
        error_message = self.faker.sentence()

        async def handle_to_success(route: Route):
            if route.request.method == "GET":
                await route.continue_()
                return

            response_to_error: Response[None] = Response.fail(error_message)
            await route.fulfill(
                status=200,
                body=response_to_error.model_dump_json(),
                headers={"Content-Type": "application/json"},
            )

        new_content = self.faker.paragraph()
        await self.page.route("**/api/v1/updatable-objects/test", handle_to_success)
        await self.page.goto(self.home_url)
        await self.page.select_option("#which-file", "test")
        await sleep(1)

        textarea = await self.page.wait_for_selector("#file-content", timeout=5000)
        assert textarea is not None
        await textarea.fill(new_content)

        # Act
        submit_button = await self.page.wait_for_selector("#save-file", timeout=5000)
        assert submit_button is not None
        await submit_button.click()

        # Assert
        feedback_panel = await self.page.query_selector("#feedback-panel")
        assert feedback_panel is not None
        feedback_message = await feedback_panel.inner_text()
        feedback_message = feedback_message.strip()
        self.assertIn(error_message, feedback_message)
