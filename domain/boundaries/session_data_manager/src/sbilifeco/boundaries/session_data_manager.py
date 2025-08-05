from typing import Protocol
from sbilifeco.models.base import Response


class ISessionDataManager(Protocol):
    async def update_session_data(self, session_id: str, data: str) -> Response[None]:
        raise NotImplementedError("Method must be implemented by subclasses")

    async def get_session_data(self, session_id: str) -> Response[str]:
        raise NotImplementedError("Method must be implemented by subclasses")

    async def delete_session_data(self, session_id: str) -> Response[None]:
        raise NotImplementedError("Method must be implemented by subclasses")

    async def delete_all_session_data(self) -> Response[None]:
        raise NotImplementedError("Method must be implemented by subclasses")
