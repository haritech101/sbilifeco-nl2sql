from __future__ import annotations
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.user_flows.query_flow import IQueryFlow
from sbilifeco.cp.query_flow.paths import Paths, QueryRequest
from sbilifeco.models.base import Response


class QueryFlowHttpService(HttpServer):
    def __init__(self):
        HttpServer.__init__(self)

    def set_query_flow(self, query_flow: IQueryFlow) -> QueryFlowHttpService:
        self.query_flow = query_flow
        return self

    async def listen(self):
        await HttpServer.listen(self)

    async def stop(self):
        await HttpServer.stop(self)

    def build_routes(self) -> None:
        HttpServer.build_routes(self)

        @self.post(Paths.SESSIONS)
        async def create_session() -> Response[str]:
            try:
                return await self.query_flow.start_session()
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.SESSION_BY_ID)
        async def delete_session(session_id: str) -> Response[None]:
            try:
                return await self.query_flow.stop_session(session_id)
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.SESSION_RESET)
        async def reset_session(session_id: str) -> Response[None]:
            try:
                return await self.query_flow.reset_session(session_id)
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.QUERIES)
        async def query(session_id: str, req: QueryRequest) -> Response[str]:
            try:
                return await self.query_flow.query(
                    req.db_id,
                    session_id,
                    req.question,
                    req.is_pii_allowed,
                    req.with_thoughts,
                )
            except Exception as e:
                return Response.error(e)
