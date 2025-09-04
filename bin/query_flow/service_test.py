from ctypes.util import test
import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from service import QueryFlowMicroservice
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from uuid import uuid4


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        test_type = getenv(EnvVars.test_type, Defaults.test_type)

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        self.service = QueryFlowMicroservice()

        if test_type == "unit":
            await self.service.run()

        self.client = QueryFlowHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(http_port)

    async def asyncTearDown(self) -> None: ...

    async def _test_with(self, question: str) -> None:
        # Arrange
        # db_id = "0bac8529-2da1-44f9-ad6e-0964be4e7d54"
        db_id = "ed0d5b22-2d57-41df-a98d-a5f9ddf92a38"
        session_id = uuid4().hex

        # Act
        query_response = await self.client.query(db_id, session_id, question)

        # Assert
        self.assertTrue(query_response.is_success, query_response.message)
        assert (
            query_response.payload is not None
        ), "Query response data should not be None"
        print(query_response.payload)
        self.assertIn(
            "select",
            query_response.payload.lower(),
            "Query response should contain 'select'",
        )

    async def test_non_join_query(self) -> None:
        # Arrange
        question = "Total Actual NBP from Retal Ageny in bengalor"

        # Act and assert
        await self._test_with(question)

    async def test_join_query(self) -> None:
        # Arrange
        question = "NBP Budget achievement YTD for PMJJBY segment"

        # Act and assert
        await self._test_with(question)
