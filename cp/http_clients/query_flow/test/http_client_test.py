from operator import is_
from random import randint
import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from sbilifeco.cp.query_flow.http_server import QueryFlowHttpService
from sbilifeco.models.base import Response
from sbilifeco.boundaries.query_flow import IQueryFlow
from faker import Faker
from uuid import uuid4


class HttpClientTest(IsolatedAsyncioTestCase):
    FLOW_PORT = 10000

    async def asyncSetUp(self) -> None:
        self.flow: IQueryFlow = AsyncMock(spec=IQueryFlow)

        self.http_service = QueryFlowHttpService().set_query_flow(self.flow)
        self.http_service.set_http_port(self.FLOW_PORT)
        await self.http_service.listen()

        self.client = QueryFlowHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(self.FLOW_PORT)

        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        await self.http_service.stop()

    async def test_start_session(self):
        # Arrange
        session_id = uuid4().hex
        patched_start_session_method = patch.object(
            self.flow, "start_session", return_value=Response.ok(session_id)
        ).start()

        # Act
        response = await self.client.start_session()

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, session_id)

        patched_start_session_method.assert_called_once_with()

    async def test_stop_session(self):
        # Arrange
        session_id = uuid4().hex
        patched_stop_session_method = patch.object(
            self.flow, "stop_session", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.stop_session(session_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        patched_stop_session_method.assert_called_once_with(session_id)

    async def test_reset_session(self):
        # Arrange
        session_id = uuid4().hex
        patched_reset_session_method = patch.object(
            self.flow, "reset_session", return_value=Response.ok(None)
        ).start()

        # Act
        response = await self.client.reset_session(session_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        patched_reset_session_method.assert_called_once_with(session_id)

    async def test_query(self):
        # Arrange
        db_id = uuid4().hex
        session_id = uuid4().hex
        question = self.faker.sentence()
        answer = self.faker.sentence()
        is_pii_allowed = True if randint(0, 1) == 1 else False
        with_thoughts = randint(0, 1) == 1

        patched_query_method = patch.object(
            self.flow, "query", return_value=Response.ok(answer)
        ).start()

        # Act
        response = await self.client.query(
            db_id, session_id, question, is_pii_allowed, with_thoughts
        )

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, answer)

        patched_query_method.assert_called_once_with(
            db_id, session_id, question, is_pii_allowed, with_thoughts
        )
