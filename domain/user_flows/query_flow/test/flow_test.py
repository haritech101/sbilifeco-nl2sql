import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.llm.http_client import LLMHttpClient


class FlowTest(IsolatedAsyncioTestCase):
    STORAGE_PORT = 11202
    LLM_PORT = 11203

    async def asyncSetUp(self) -> None:
        self.storage = MetadataStorageHttpClient()
        self.storage.set_proto("http").set_host("localhost").set_port(self.STORAGE_PORT)

        self.llm = LLMHttpClient()
        self.llm.set_proto("http").set_host("localhost").set_port(self.LLM_PORT)

        self.flow = QueryFlow().set_metadata_storage(self.storage).set_llm(self.llm)

        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_query_flow(self) -> None:
        # Arrange
        dbs_response = await self.storage.get_dbs()
        assert (
            dbs_response.is_success
        ), f"Failed to retrieve databases: {dbs_response.message}"
        assert dbs_response.payload is not None, "Databases payload should not be None"
        assert len(dbs_response.payload) > 0
        dbId = dbs_response.payload[0].id

        question = "What is the NBP in Delhi in May?"

        # Act
        response = await self.flow.query(dbId, question)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        print(response.payload)
        # self.assertIn(
        #     "SELECT", response.payload, "Response payload should contain a SQL query"
        # )

    async def test_reset(self) -> None:
        # Act
        reset_response = await self.flow.reset()

        # Assert
        self.assertTrue(reset_response.is_success, reset_response.message)
