from __future__ import annotations
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from sbilifeco.models.base import Response
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.llm.paths import Paths
from sbilifeco.boundaries.llm import ChatMessage
from sbilifeco.models.db_metadata import DB, Table, Field
from sbilifeco.models.base import Response
from fastapi import Request as FastAPIRequest


class LLMMicroservice(HttpServer):
    def __init__(self):
        HttpServer.__init__(self)
        self.llm: ILLM

    def set_llm(self, llm: ILLM) -> LLMMicroservice:
        self.llm = llm
        return self

    async def listen(self) -> None:
        await HttpServer.listen(self)

    async def stop(self) -> None:
        await HttpServer.stop(self)

    def build_routes(self) -> None:
        @self.post(Paths.CONTEXT)
        async def add_context(context: list[ChatMessage]) -> Response[None]:
            try:
                return await self.llm.add_context(context)
            except Exception as e:
                return Response.error(e)

        @self.put(Paths.METADATA)
        async def set_metadata(db: DB) -> Response[None]:
            try:
                return await self.llm.set_metadata(db)
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.QUERIES)
        async def generate_query(req: FastAPIRequest) -> Response[str]:
            try:
                return await self.llm.generate_sql((await req.body()).decode("utf-8"))
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.RESET_REQUESTS)
        async def reset_requests() -> Response[None]:
            try:
                return await self.llm.reset_context()
            except Exception as e:
                return Response.error(e)
