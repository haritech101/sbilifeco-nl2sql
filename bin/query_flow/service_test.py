from asyncio import sleep
import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from pprint import pprint
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here
from service import QueryFlowMicroservice
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from uuid import uuid4
from pathlib import Path


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        self.test_type = getenv(EnvVars.test_type, Defaults.test_type)

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        staging_host = getenv(EnvVars.staging_host, Defaults.staging_host)
        self.db_id = getenv(EnvVars.db_id, "")

        if self.test_type == "unit":
            self.service = QueryFlowMicroservice()
            await self.service.run()

        self.client = QueryFlowHttpClient()
        host = staging_host if self.test_type == "staging" else "localhost"
        self.client.set_proto("http").set_host(host).set_port(http_port)

    async def asyncTearDown(self) -> None: ...

    async def _test_with(self, question: str, with_thoughts: bool = True) -> str:
        # Arrange
        session_id = uuid4().hex

        # Act
        query_response = await self.client.query(
            self.db_id, session_id, question, with_thoughts
        )

        # Assert
        self.assertTrue(query_response.is_success, query_response.message)
        assert (
            query_response.payload is not None
        ), "Query response data should not be None"

        print("\nLLM's final response follows:\n\n", flush=True)
        print(query_response.payload, flush=True)
        print("\nEnd of LLM's final response\n\n", flush=True)

        self.assertIn(
            "select",
            query_response.payload.lower(),
            "Query response should contain 'select'",
        )

        return query_response.payload

    async def test_starts_fine(self) -> None: ...

    async def test_metadata_query(self) -> None:
        # Arrange
        question = getenv(EnvVars.metadata_query, "")

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_master_table_query(self) -> None:
        # Arrange
        question = getenv(EnvVars.master_table_query, "")

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_single_table_query(self) -> None:
        # Arrange
        question = getenv(EnvVars.single_table_query, "")

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_joined_tables_query(self) -> None:
        # Arrange
        question = getenv(EnvVars.joined_tables_query, "")

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_infer_schema(self) -> None:
        # Arrange
        question = "Please tell me what you have inferred."

        # Act and assert
        llm_reply = await self._test_with(question, with_thoughts=False)

        with open(".local/inferred.md", "w") as inference:
            inference.write(llm_reply)

    async def test_tool_call(self) -> None:
        # Arrange
        question = "Count the number of policies issued in Mumbai"
        session_id = uuid4().hex

        # Act
        service_response = await self.client.query(
            self.db_id, session_id, question, with_thoughts=True
        )

        # Assert
        self.assertTrue(service_response.is_success, service_response.message)

        answer = service_response.payload
        assert answer is not None
        self.assertTrue(answer)
        print(f"LLM's reply follows: ***\n\n{answer}\n\n***\n", flush=True)
        self.assertIn("count_by_named_division", answer)

    async def test_conversation(self) -> None:
        # Arrange
        session_id = uuid4().hex

        questions = [
            "Give me the list of policies issued in Mumbai",
            "August 2025",
            "Narrow down to independence day",
            "What about Diwali of the same year?",
        ]

        # Act & Assert
        for question in questions:
            service_response = await self.client.query(
                self.db_id, session_id, question, with_thoughts=True
            )

            self.assertTrue(service_response.is_success, service_response.message)

            answer = service_response.payload
            assert answer is not None
            self.assertTrue(answer)
            print(f"LLM's reply follows: ***\n\n{answer}\n\n***\n", flush=True)
