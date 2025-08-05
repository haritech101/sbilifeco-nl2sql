from typing import Protocol
from sbilifeco.models.base import Response


class IQueryFlow(Protocol):
    async def start_session(self) -> Response[str]:
        raise NotImplementedError()

    async def stop_session(self) -> Response[None]:
        raise NotImplementedError()

    async def reset_session(self) -> Response[None]:
        raise NotImplementedError()

    async def query(self, dbId: str, question: str) -> Response[str]:
        raise NotImplementedError()

    async def reset(self) -> Response[None]:
        raise NotImplementedError()
