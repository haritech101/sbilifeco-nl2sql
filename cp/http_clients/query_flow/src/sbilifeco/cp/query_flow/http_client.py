from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.query_flow import IQueryFlow
from sbilifeco.models.base import Response
from requests import Request
from sbilifeco.cp.query_flow.paths import Paths, QueryRequest


class QueryFlowHttpClient(HttpClient, IQueryFlow):
    def __init__(self) -> None:
        HttpClient.__init__(self)

    async def query(self, dbId: str, question: str) -> Response[str]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.QUERIES}",
                    json=QueryRequest(db_id=dbId, question=question).model_dump(),
                )
            )
        except Exception as e:
            return Response.error(e)
