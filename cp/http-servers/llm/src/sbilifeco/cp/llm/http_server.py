from __future__ import annotations
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from sbilifeco.models.base import Response
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.llm.paths import Paths, LLMQuery
from sbilifeco.boundaries.llm import ChatMessage
from sbilifeco.models.db_metadata import DB, Table, Field
from sbilifeco.models.base import Response


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
        @self.post(Paths.QUERIES)
        async def generate_query(query: LLMQuery) -> Response[str]:
            try:
                return await self.llm.generate_reply(query.context)
            except Exception as e:
                return Response.error(e)
