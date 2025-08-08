from typing import Protocol
from pydantic import BaseModel
from sbilifeco.models.base import Response


class ChatMessage(BaseModel):
    role: str
    content: str


class ILLM(Protocol):
    async def generate_reply(self, context: str) -> Response[str]:
        raise NotImplementedError()
