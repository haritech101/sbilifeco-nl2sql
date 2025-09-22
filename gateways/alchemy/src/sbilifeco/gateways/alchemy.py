from __future__ import annotations

from asyncio import get_running_loop
from typing import Any, Callable

from sbilifeco.boundaries.sql_db import ISqlDb
from sbilifeco.models.base import Response
from sqlalchemy import Engine, create_engine, text


class Alchemy(ISqlDb):
    def __init__(self) -> None:
        self.connection_string = ""
        self.engine: Engine

    def set_connection_string(self, connection_string: str) -> Alchemy:
        self.connection_string = connection_string
        return self

    async def async_init(self) -> None:
        if not self.connection_string:
            raise ValueError("Connection string is not set.")

        self.engine = create_engine(self.connection_string)

    async def _ensure_connection(self, wrapped: Callable, *args, **kwargs) -> Any:
        if not self.engine:
            await self.async_init()
        return await wrapped(*args, **kwargs)

    async def async_shutdown(self) -> None:
        self.engine.dispose()

    async def _execute_query(self, query: str) -> Response[Any]:
        try:
            with self.engine.connect() as connection:
                result = await get_running_loop().run_in_executor(
                    None, connection.execute, text(query)
                )
                return Response.ok(result.mappings().all())
        except Exception as e:
            return Response.error(e)

    async def execute_query(self, query: str) -> Response[list[dict[str, Any]]]:
        try:
            return await self._ensure_connection(self._execute_query, query)
        except Exception as e:
            return Response.error(e)
