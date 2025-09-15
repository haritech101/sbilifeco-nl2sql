from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.query_flow import IQueryFlow
from sbilifeco.models.base import Response
from requests import Request
from sbilifeco.cp.query_flow.paths import Paths, QueryRequest


class QueryFlowHttpClient(HttpClient, IQueryFlow):
    def __init__(self) -> None:
        HttpClient.__init__(self)

    async def start_session(self) -> Response[str]:
        try:
            return await self.request_as_model(
                Request(method="POST", url=f"{self.url_base}{Paths.SESSIONS}", json={})
            )
        except Exception as e:
            return Response.error(e)

    async def stop_session(self, session_id: str) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="DELETE",
                    url=f"{self.url_base}{Paths.SESSION_BY_ID.format(session_id=session_id)}",
                )
            )
        except Exception as e:
            return Response.error(e)

    async def reset_session(self, session_id: str) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.SESSION_RESET.format(session_id=session_id)}",
                    json={},
                )
            )
        except Exception as e:
            return Response.error(e)

    async def query(
        self, dbId: str, session_id: str, question: str, with_thoughts: bool = False
    ) -> Response[str]:
        try:
            req = Request(
                method="POST",
                url=f"{self.url_base}{Paths.QUERIES.format(session_id=session_id)}",
                json=QueryRequest(
                    db_id=dbId, question=question, with_thoughts=with_thoughts
                ).model_dump(),
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)
