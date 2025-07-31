import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from sbilifeco.cp.query_flow.microservice import QueryFlowMicroservice
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.models.base import Response
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient


class HttpClientTest(IsolatedAsyncioTestCase):
    LOCATION = "inbuilt"  # "inbuilt" "standalone"
    LLM_PORT = 11003
    STORAGE_PORT = 11001
    if LOCATION == "inbuilt":
        FLOW_PORT = 9000
    else:
        FLOW_PORT = 11004

    async def asyncSetUp(self) -> None:
        self.llm = LLMHttpClient()
        self.llm.set_proto("http").set_host("localhost").set_port(self.LLM_PORT)

        self.storage = MetadataStorageHttpClient()
        self.storage.set_proto("http").set_host("localhost").set_port(self.STORAGE_PORT)

        self.flow = QueryFlow()
        self.flow.set_llm(self.llm).set_metadata_storage(self.storage)

        if self.LOCATION == "inbuilt":
            self.microservice = QueryFlowMicroservice()
            self.microservice.set_query_flow(self.flow).set_http_port(self.FLOW_PORT)
            await self.microservice.listen()

        self.client = QueryFlowHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(self.FLOW_PORT)

    async def asyncTearDown(self) -> None:
        if self.LOCATION == "inbuilt":
            await self.microservice.stop()

    async def test_query(self):
        # Arrange
        dbs_response = await self.storage.get_dbs()
        assert dbs_response.is_success, dbs_response.message
        assert dbs_response.payload is not None, "Database list is null"
        db = dbs_response.payload[0]

        question = "What is the real time cashiering for the current month in Mumbai, Delhi and Chennai?"

        # Act
        response = await self.client.query(db.id, question)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        print(response.payload)
        self.assertIn("select", response.payload.lower())

    async def test_reset(self) -> None:
        # Act
        reset_response = await self.client.reset()

        # Assert
        self.assertTrue(reset_response.is_success, reset_response.message)
