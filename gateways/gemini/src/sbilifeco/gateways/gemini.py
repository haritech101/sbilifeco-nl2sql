from __future__ import annotations
from json import dumps
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from google.genai import Client
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB


class Gemini(ILLM):
    def __init__(self):
        self.model: str = "gemini-1.5-flash"
        self.api_key: str
        self.client: Client
        self.context: list[str] = [
            "You are a SQL expert. You will be given a question and you will generate the SQL query to answer it.\n",
            "You will be given the database metadata, which includes the database name, description, tables, and fields.\n",
            "You will also be given the context of the conversation, which includes previous questions and answers.\n",
            "You will generate the SQL query based on the question and the database metadata.\n",
            "You will return just the SQL query without any other adornments\n",
        ]

    def set_model(self, model: str) -> Gemini:
        self.model = model
        return self

    def set_api_key(self, api_key: str) -> Gemini:
        self.api_key = api_key
        return self

    async def async_init(self) -> None:
        self.client = Client(api_key=self.api_key)

    async def add_context(self, context: list[ChatMessage]) -> Response[None]:
        try:
            self.context.extend([message.content for message in context])
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def set_metadata(self, db: DB) -> Response[None]:
        try:
            self.context.append(
                "The query will be based on the following database metadata:\n"
            )
            self.context.append(f"Database name: {db.name}\n")
            self.context.append(f"Database description: {db.description}\n")
            if db.tables is not None:
                for table in db.tables:
                    self.context.append(f"\tTable name: {table.name}\n")
                    self.context.append(f"\tTable description: {table.description}\n")
                    if table.fields is not None:
                        for field in table.fields:
                            self.context.append(
                                f"\t\tField name: {field.name}, type: {field.type}\n"
                            )
                            self.context.append(
                                f"\t\tField description: {field.description}\n"
                            )
                            self.context.append(
                                f"\t\tOther names for field '{field.name}': {field.aka}\n"
                            )
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def generate_sql(self, question: str) -> Response[str]:
        try:
            challenge = "".join([item for item in self.context])
            line = f"\nGenerate a query against this question/statement:\n{question}\n"
            challenge += line
            print(challenge)

            self.context.append(line)

            gemini_response = self.client.models.generate_content(
                model=self.model, contents=challenge
            )
            answer = (gemini_response.text or "").strip()
            self.context.append(answer)

            return Response.ok(answer)
        except Exception as e:
            return Response.error(e)
