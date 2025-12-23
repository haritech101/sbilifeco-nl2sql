from __future__ import annotations
from typing import Protocol
from sbilifeco.models.base import Response


class IObjectReadUpdate(Protocol):
    async def read(self, object_id: str) -> Response[bytes]: ...
    async def update(self, object_id: str, content: bytes) -> Response[None]: ...
