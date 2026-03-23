import sys

sys.path.append("./src")

from os import getenv
from asyncio import sleep, gather
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from uuid import uuid4
from random import randint, random
from faker import Faker
from datetime import datetime, date
from pprint import pprint, pformat
from sbilifeco.models.base import Response

# Import the necessary service(s) here
from sbilifeco.cp.query_flow_listener.log_directory_presenter import (
    LogDirectoryPresenter,
)
from sbilifeco.boundaries.query_flow import QueryFlowAnswer
from pathlib import Path
from os import unlink


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        log_dir = getenv(EnvVars.log_dir, Defaults.log_dir)

        # Initialise the service(s) here
        self.faker = Faker()

        if self.test_type == "unit":
            self.service = LogDirectoryPresenter().set_log_directory(log_dir)
            await self.service.async_init()
            self.log_file_path = (
                Path(getenv(EnvVars.log_dir, Defaults.log_dir))
                / f"{date.today().isoformat()}.csv"
            )

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        unlink(self.log_file_path)
        patch.stopall()

    async def test_present(self) -> None:
        # Arrange
        answer = QueryFlowAnswer(
            session_id=uuid4().hex,
            db_id=self.faker.word(),
            question=self.faker.sentence(),
            answer=self.faker.paragraph(),
            response_time_seconds=random() * 5,
        )

        # Act
        await self.service.on_answer(answer)

        # Assert
        self.assertTrue(
            self.log_file_path.exists(), f"Log file {self.log_file_path} does not exist"
        )

        is_db_id_found = False
        is_question_found = False
        is_answer_found = False
        with open(self.log_file_path, "r") as f:
            for line in f:
                if answer.db_id in line:
                    is_db_id_found = True
                if answer.question in line:
                    is_question_found = True
                if answer.answer in line:
                    is_answer_found = True
                if is_db_id_found and is_question_found and is_answer_found:
                    break
        self.assertTrue(
            is_db_id_found,
            f"DB ID '{answer.db_id}' not found in log file {self.log_file_path}",
        )
        self.assertTrue(
            is_question_found,
            f"Question '{answer.question}' not found in log file {self.log_file_path}",
        )
        self.assertTrue(
            is_answer_found,
            f"Answer '{answer.answer}' not found in log file {self.log_file_path}",
        )
