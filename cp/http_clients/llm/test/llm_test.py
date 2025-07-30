import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from sbilifeco.gateways.ollama import Ollama
from sbilifeco.cp.llm.microservice import LLMMicroservice
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.models.db_metadata import DB, Table, Field
from sbilifeco.boundaries.llm import ChatMessage
from uuid import uuid4


class LLMTest(IsolatedAsyncioTestCase):
    HTTP_PORT = 8181

    async def asyncSetUp(self) -> None:
        self.ollama = Ollama()
        self.ollama.set_host("localhost").set_model("codellama")
        await self.ollama.async_init()

        self.microservice = LLMMicroservice()
        self.microservice.set_llm(self.ollama).set_http_port(self.HTTP_PORT)

        await self.microservice.listen()

        self.client = LLMHttpClient()
        self.client.set_proto("http").set_host("localhost").set_port(self.HTTP_PORT)

    async def asyncTearDown(self) -> None:
        await self.microservice.stop()
        return await super().asyncTearDown()

    async def test_reset(self) -> None:
        # Act
        response = await self.client.reset_context()

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertIsNone(response.payload)

    async def test_sequence(self) -> None:
        db = DB(
            id=uuid4().hex,
            name="shopping",
            description="Database for a shopping application",
            tables=[
                Table(
                    id=uuid4().hex,
                    name="products",
                    description="Table containing product information",
                    fields=[
                        Field(id=uuid4().hex, name="id", type="text"),
                        Field(id=uuid4().hex, name="name", type="text"),
                        Field(id=uuid4().hex, name="price", type="number"),
                    ],
                ),
                Table(
                    id=uuid4().hex,
                    name="orders",
                    description="Table containing order information",
                    fields=[
                        Field(id=uuid4().hex, name="id", type="text"),
                        Field(id=uuid4().hex, name="product_id", type="text"),
                        Field(id=uuid4().hex, name="quantity", type="text"),
                    ],
                ),
            ],
        )

        await self.client.set_metadata(db)
        await self.client.add_context(
            [
                ChatMessage(
                    role="system", content="Assume that the database is in MySQL\n\n"
                )
            ]
        )
        question = "How can I get the names of all products and how much each was sold?"

        response = await self.client.generate_sql(question)
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        print(response.payload)
        self.assertIn("select", response.payload.lower())
