from os import getenv
from unittest import IsolatedAsyncioTestCase

from dotenv import load_dotenv
from sbilifeco.gateways.gemini import Gemini
from sbilifeco.models.db_metadata import DB, Table, Field


class GeminiTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()
        api_key = getenv("API_KEY", "")
        model = getenv("MODEL", "gemini-1.5-flash")

        self.gemini = Gemini().set_api_key(api_key).set_model(model)
        await self.gemini.async_init()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_generate_sql(self):
        # Arrange
        db = DB(
            name="payroll",
            description="Payroll database for company employees",
            tables=[
                Table(
                    name="employees",
                    description="Table containing employee information",
                    fields=[
                        Field(
                            name="id",
                            type="integer",
                            description="Unique identifier for each employee",
                            aka="employee_id, emp_id",
                        ),
                        Field(
                            name="name",
                            type="text",
                            description="Name of the employee",
                            aka="full_name",
                        ),
                        Field(
                            name="department",
                            type="text",
                            description="Department where the employee works",
                            aka="dept",
                        ),
                    ],
                ),
                Table(
                    name="salaries",
                    description="Table containing employee salary information",
                    fields=[
                        Field(
                            name="employee_id",
                            type="integer",
                            description="Unique identifier for each employee",
                            aka="id, emp_id",
                        ),
                        Field(
                            name="salary",
                            type="decimal",
                            description="Salary of the employee",
                            aka="pay, compensation",
                        ),
                    ],
                ),
            ],
        )
        await self.gemini.set_metadata(db)

        question = "Which department has the highest average salary?"

        # Act
        response = await self.gemini.generate_sql(question)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Response payload should not be None"
        print(response.payload)
        self.assertIn(
            "select", response.payload.lower(), "Response should contain 'blue'"
        )
