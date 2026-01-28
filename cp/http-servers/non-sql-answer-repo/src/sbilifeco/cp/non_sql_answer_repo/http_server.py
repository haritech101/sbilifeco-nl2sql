from __future__ import annotations
from typing import Sequence, Annotated
from sbilifeco.models.base import Response
from fastapi import Query

# Import other required contracts/modules here
from sbilifeco.boundaries.query_flow import (
    INonSqlAnswerRepo,
    NonSqlAnswer,
    GetNonSqlAnswersRequest,
)
from sbilifeco.cp.non_sql_answer_repo.paths import Paths
from sbilifeco.cp.common.http.server import HttpServer


class NonSQLAnswerRepoHTTPServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.repo: INonSqlAnswerRepo

    def set_repo(self, repo: INonSqlAnswerRepo) -> NonSQLAnswerRepoHTTPServer:
        self.repo = repo
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.get(Paths.BASE)
        async def get_non_sql_answers(
            request: Annotated[GetNonSqlAnswersRequest, Query()],
        ) -> Response[Sequence[NonSqlAnswer]]:
            try:
                # Validate request
                ...

                # Triage request
                ...

                # Gateway call
                res = await self.repo.get_non_sql_answers(request)

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)
