from typing import Protocol
from pydantic import BaseModel
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB


class ChatMessage(BaseModel):
    role: str
    content: str


class ILLM(Protocol):
    async def set_preamble(self, instruction: str) -> Response[None]:
        raise NotImplementedError()

    async def set_metadata(self, db: DB) -> Response[None]:
        raise NotImplementedError()

    async def set_postamble(self, instruction: str) -> Response[None]:
        raise NotImplementedError()

    async def add_context(self, context: list[ChatMessage]) -> Response[None]:
        raise NotImplementedError()

    async def reset_context(self) -> Response[None]:
        raise NotImplementedError()

    async def generate_sql(self, question: str) -> Response[str]:
        raise NotImplementedError()
