from __future__ import annotations
from typing import Sequence
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.cp.query_flow_answer_repo.paths import Paths
from sbilifeco.boundaries.query_flow import (
    GetQueryFlowAnswersRequest,
    IQueryFlowAnswerRepo,
    QueryFlowAnswer,
)


class QueryFlowAnswerRepoHttpClient(HttpClient, IQueryFlowAnswerRepo):
    def __init__(self):
        HttpClient.__init__(self)

    async def get_query_flow_answers(
        self, request: GetQueryFlowAnswersRequest
    ) -> Response[Sequence[QueryFlowAnswer]]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.BASE}"
            req = Request(url=url, method="GET", params=request.model_dump())

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            if res.payload is not None:
                res.payload = [
                    QueryFlowAnswer.model_validate(item) for item in res.payload
                ]

            # Return response
            return res
        except Exception as e:
            return Response.error(e)
