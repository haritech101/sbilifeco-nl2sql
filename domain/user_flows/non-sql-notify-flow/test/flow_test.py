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
from sbilifeco.flows.non_sql_notify_flow import NonSqlNotifyFlow
from sbilifeco.boundaries.query_flow import INonSqlAnswerRepo, NonSqlAnswer
from sbilifeco.boundaries.non_sql_notify_flow import INonSqlPresenter


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)

        # Initialise the service(s) here
        self.faker = Faker()

        self.repo = AsyncMock(spec=INonSqlAnswerRepo)
        self.presenter = AsyncMock(spec=INonSqlPresenter)

        if self.test_type == "unit":
            self.service = NonSqlNotifyFlow().set_non_sql_answer_repo(self.repo)
            self.service.add_presenter(self.presenter)
            await self.service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        if self.test_type == "unit":
            await self.service.async_shutdown()
        patch.stopall()

    async def test_fetch_and_notify(self) -> None:
        # Arrange
        answers = [
            NonSqlAnswer(
                session_id=uuid4().hex,
                db_id=uuid4().hex,
                question=self.faker.sentence(),
                answer=self.faker.paragraph(),
            )
            for _ in range(randint(2, 4))
        ]

        fn_fetch = patch.object(
            self.repo, "get_non_sql_answers", return_value=Response.ok(answers)
        ).start()

        fn_present = patch.object(self.presenter, "present", return_value=None).start()

        # Act
        await self.service.fetch_and_notify()

        # Assert
        fn_fetch.assert_called_once()
        fn_present.assert_called_once_with(answers)
