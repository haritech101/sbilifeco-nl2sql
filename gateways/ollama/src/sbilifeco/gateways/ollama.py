from __future__ import annotations
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from ollama import AsyncClient
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB


class Ollama(ILLM):
    def __init__(self):
        self.client: AsyncClient
        self.host = "localhost"
        self.model = ""
        self.context: list[ChatMessage] = []

    def set_model(self, model: str) -> Ollama:
        """Set the model to be used for the LLM."""
        self.model = model
        return self

    def set_host(self, host: str) -> Ollama:
        """Set the host for the LLM."""
        self.host = host
        return self

    async def async_init(self) -> None:
        self.client = AsyncClient(self.host)

    async def add_context(self, context: list[ChatMessage]) -> Response[None]:
        try:
            self.context.extend(context)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def set_metadata(self, db: DB) -> Response[None]:
        try:
            db_context = (
                f"Database Name: {db.name}\n"
                f"Database Description: {db.description or "None"}\n"
                "Database Tables:\n"
            )
            for table in db.tables or []:
                db_context += f"\tTable Name: {table.name}\n"
                f"\tTable Description: {table.description or "None"}\n"
                "\tTable Fields:\n"
                for field in table.fields or []:
                    db_context += (
                        f"\t\tField Name: {field.name}\n"
                        f"\t\tField Type: {field.type or "None"}\n"
                        f"\t\tField Description: {field.description or "None"}\n"
                        f"\t\tOther Names fo field '{field.name}': {field.aka or "None"}\n\n"
                    )

            print(db_context)

            self.context.append(
                ChatMessage(
                    role="system",
                    content=f"You are a SQL generation assistant.\n"
                    f"You have access to the following database metadata:\n\n"
                    f"{db_context}\n\n"
                    f"Please generate the SQL query for the questions asked below.\n\n",
                )
            )
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def generate_sql(self, question: str) -> Response[str]:
        try:
            self.context.append(ChatMessage(role="user", content=question))
            normalised_context = [piece.model_dump() for piece in self.context]

            reply = await self.client.chat(
                model=self.model, messages=normalised_context
            )

            reply_message = ChatMessage(
                role=reply.message.role, content=(reply.message.content or "").strip()
            )
            self.context.append(reply_message)

            return Response.ok(reply_message.content)
        except Exception as e:
            return Response.error(e)
