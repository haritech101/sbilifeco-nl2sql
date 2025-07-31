from __future__ import annotations
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.user_flows.query_flow import IQueryFlow
from sbilifeco.cp.query_flow.paths import Paths, QueryRequest
from sbilifeco.models.base import Response


class QueryFlowMicroservice(HttpServer):
    def __init__(self):
        HttpServer.__init__(self)

    def set_query_flow(self, query_flow: IQueryFlow) -> QueryFlowMicroservice:
        self.query_flow = query_flow
        return self

    async def listen(self):
        await HttpServer.listen(self)

    async def stop(self):
        await HttpServer.stop(self)

    def build_routes(self) -> None:
        HttpServer.build_routes(self)

        @self.post(Paths.QUERIES)
        async def query(req: QueryRequest) -> Response[str]:
            try:
                return await self.query_flow.query(req.db_id, req.question)
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.RESET)
        async def reset() -> Response[None]:
            try:
                return await self.query_flow.reset()
            except Exception as e:
                return Response.error(e)
