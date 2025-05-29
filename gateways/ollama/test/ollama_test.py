from unittest import IsolatedAsyncioTestCase
from sbilifeco.gateways.ollama import Ollama
from sbilifeco.models.db_metadata import DB, Table, Field
from uuid import uuid4
from faker import Faker


class OllamaTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ollama = Ollama()
        self.ollama.set_model("codellama")
        self.ollama.set_host("localhost")
        self.faker = Faker()

        db = DB(
            id=uuid4().hex,
            name="HR",
            description="Acme company's HR database",
            tables=[
                Table(
                    name="employees",
                    description="Employee records",
                    fields=[
                        Field(name="id", type="text", description="Employee ID"),
                        Field(name="name", type="text", description="Employee name"),
                        Field(
                            name="department",
                            type="text",
                            description="Department of the employee",
                        ),
                        Field(
                            name="salary", type="number", description="Employee salary"
                        ),
                    ],
                )
            ],
        )

        self.ollama.set_metadata(db)
        await self.ollama.async_init()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_generate_query(self) -> None:
        # Arrange
        questions = [
            "What is the total money spent by the company on salaries?",
            "And what about mean?",
            "And what about median?",
        ]

        for question in questions:
            # Act
            response = await self.ollama.generate_sql(question)

            # Assert
            self.assertTrue(response.is_success, response.message)
            assert response.payload is not None, "Response payload should not be None"
            print(response.payload)
            self.assertIn("SELECT", response.payload)
