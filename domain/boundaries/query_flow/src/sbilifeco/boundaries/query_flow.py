from typing import Protocol
from sbilifeco.models.base import Response


class IQueryFlow(Protocol):
    async def start_session(self) -> Response[str]:
        raise NotImplementedError()

    async def stop_session(self, session_id: str) -> Response[None]:
        raise NotImplementedError()

    async def reset_session(self, session_id: str) -> Response[None]:
        raise NotImplementedError()

    async def query(
        self,
        dbId: str,
        session_id: str,
        question: str,
        is_pii_allowed=False,
        with_thoughts: bool = False,
    ) -> Response[str]:
        raise NotImplementedError()
