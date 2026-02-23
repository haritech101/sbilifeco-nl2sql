from __future__ import annotations
from typing import Sequence, Annotated
from sbilifeco.models.base import Response
from fastapi import Query

# Import other required contracts/modules here
from sbilifeco.boundaries.query_flow import (
    IQueryFlowAnswerRepo,
    QueryFlowAnswer,
    GetQueryFlowAnswersRequest,
)
from sbilifeco.cp.query_flow_answer_repo.paths import Paths
from sbilifeco.cp.common.http.server import HttpServer


class QueryFlowAnswerRepoHTTPServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.repo: IQueryFlowAnswerRepo

    def set_repo(self, repo: IQueryFlowAnswerRepo) -> QueryFlowAnswerRepoHTTPServer:
        self.repo = repo
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.get(Paths.BASE)
        async def get_query_flow_answers(
            request: Annotated[GetQueryFlowAnswersRequest, Query()],
        ) -> Response[Sequence[QueryFlowAnswer]]:
            try:
                # Validate request
                ...

                # Triage request
                ...

                # Gateway call
                res = await self.repo.get_query_flow_answers(request)

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)
