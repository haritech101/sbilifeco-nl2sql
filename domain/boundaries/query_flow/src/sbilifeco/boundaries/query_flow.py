from typing import Protocol
from sbilifeco.models.base import Response


class IQueryFlow(Protocol):
    async def query(self, dbId: str, question: str) -> Response[str]:
        raise NotImplementedError()

    async def reset(self) -> Response[None]:
        raise NotImplementedError()
