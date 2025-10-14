from asyncio import sleep
import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
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
        self.db_id = getenv(EnvVars.db_id, "")

        if self.test_type == "unit":
            self.service = QueryFlowMicroservice()
            await self.service.run()

        self.client = QueryFlowHttpClient()
        host = "tech101.in" if self.test_type == "staging" else "localhost"
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

    async def test_non_data_query(self) -> None:
        # Arrange
        question = "Which regions are found in the south zone?"

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_non_join_query(self) -> None:
        # Arrange
        question = "Total Actual NBP from Retal Ageny in bengalor"

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_join_query(self) -> None:
        # Arrange
        question = "NBP Budget achievement YTD for PMJJBY segment"

        # Act and assert
        await self._test_with(question, with_thoughts=False)

    async def test_prompt_file_change(self) -> None:
        if self.test_type != "unit":
            self.skipTest("Skipping unit test in non-unit test type")

        # Arrange
        prompts_path = Path(getenv(EnvVars.prompts_file, ""))
        assert prompts_path != ""

        with patch.object(self.service, "set_flow_prompt") as patched_method:
            # Act
            prompts_path.touch()
            await sleep(1)

            # Assert
            patched_method.assert_called_once()

    async def test_infer_schema(self) -> None:
        # Arrange
        question = "Please tell me what you have inferred."

        # Act and assert
        llm_reply = await self._test_with(question, with_thoughts=False)

        with open(".local/inferred.md", "w") as inference:
            inference.write(llm_reply)
