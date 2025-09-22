from typing import Any, Protocol
from sbilifeco.models.base import Response


class ISqlDb(Protocol):
    async def execute_query(self, query: str) -> Response[list[dict[str, Any]]]:
        raise NotImplementedError()
