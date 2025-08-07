from __future__ import annotations
from redis import Redis as TheRedis
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.models.base import Response


class Redis(ISessionDataManager):
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
            value = self.conn.get(session_id)
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
