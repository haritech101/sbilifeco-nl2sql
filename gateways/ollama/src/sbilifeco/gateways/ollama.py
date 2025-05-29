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

    def add_context(self, context: list[ChatMessage]) -> None:
        self.context.extend(context)

    def set_metadata(self, db: DB) -> None:
        self.context.append(
            ChatMessage(
                role="system",
                content=f"You are a SQL generation assistant.\n"
                f"You have access to the following database metadata in JSON format:\n\n"
                f"{db.model_dump_json(indent=2)}\n\n"
                f"Please generate the SQL query for the questions asked below.\n\n",
            )
        )

    async def async_init(self) -> None:
        self.client = AsyncClient(self.host)

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
