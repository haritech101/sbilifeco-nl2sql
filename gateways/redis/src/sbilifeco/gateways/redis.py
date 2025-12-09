from __future__ import annotations
from typing import cast
from datetime import date, datetime
from redis import Redis as TheRedis
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.boundaries.population_counter import IPopulationCounter
from sbilifeco.models.base import Response
from pprint import pprint


class Redis(ISessionDataManager, IPopulationCounter):
    def __init__(self):
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.redis_db = 0
        self.conn: TheRedis

    def set_redis_host(self, host: str) -> Redis:
        self.redis_host = host
        return self

    def set_redis_port(self, port: int) -> Redis:
        self.redis_port = port
        return self

    def set_redis_db(self, db: int) -> Redis:
        self.redis_db = db
        return self

    async def async_init(self) -> None:
        print(
            f"Using Redis at {self.redis_host}:{self.redis_port}, with DB {self.redis_db}"
        )
        self.conn = TheRedis(
            host=self.redis_host, port=self.redis_port, db=self.redis_db
        )

    async def async_shutdown(self) -> None:
        print("Deleting test data")
        await self.delete_all_session_data()
        print("Closing Redis connection")
        if self.conn:
            self.conn.close()

    async def update_session_data(self, session_id: str, data: str) -> Response[None]:
        try:
            self.conn.set(session_id, data)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def get_session_data(self, session_id: str) -> Response[str]:
        try:
            value = cast(bytes | None, self.conn.get(session_id))
            return Response.ok("" if value is None else value.decode("utf-8"))
        except Exception as e:
            return Response.error(e)

    async def delete_session_data(self, session_id: str) -> Response[None]:
        try:
            self.conn.delete(session_id)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def delete_all_session_data(self) -> Response[None]:
        try:
            self.conn.flushdb(True)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def count_by_named_division(
        self, key: str, matching_division: str
    ) -> Response[int]:
        try:
            key = f"{key}::{matching_division}"
            return Response.ok(self._fetch_count(key))
        except Exception as e:
            pprint(e)
            return Response.ok(0)

    async def count_by_numeric_range(
        self, key: str, min_value: int | None = None, max_value: int | None = None
    ) -> Response[int]:
        try:
            key = f"{key}::{min_value if min_value is not None else ''}::{max_value if max_value is not None else ''}"
            return Response.ok(self._fetch_count(key))
        except Exception as e:
            pprint(e)
            return Response.ok(0)

    async def count_by_date_range(
        self,
        key: str,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> Response[int]:
        try:
            key = f"{key}::{start_date.isoformat() if start_date is not None else ''}::{end_date.isoformat() if end_date is not None else ''}"
            return Response.ok(self._fetch_count(key))
        except Exception as e:
            pprint(e)
            return Response.ok(0)

    async def count_by_boolean(self, key: str, true_or_false: bool) -> Response[int]:
        try:
            key = f"{key}::{true_or_false}"
            return Response.ok(self._fetch_count(key))
        except Exception as e:
            pprint(e)
            return Response.ok(0)

    def _fetch_count(self, key: str) -> int:
        print(f"Fetching population count for key: {key}")
        value_as_bytes = cast(bytes | None, self.conn.get(key))
        return int(value_as_bytes.decode("utf-8")) if value_as_bytes is not None else 0
