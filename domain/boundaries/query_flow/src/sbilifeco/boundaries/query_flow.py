from typing import Protocol, Sequence
from collections.abc import AsyncIterator
from sbilifeco.models.base import Response, BaseModel
from uuid import uuid4


class QueryFlowRequest(BaseModel):
    db_id: str
    session_id: str = uuid4().hex
    request_id: str = uuid4().hex
    question: str
    is_pii_allowed: bool = False
    with_thoughts: bool = False


class QueryFlowAnswer(BaseModel):
    session_id: str
    db_id: str
    question: str
    answer: str
    response_time_seconds: float = -1


class GetQueryFlowAnswersRequest(BaseModel):
    page_size: int = 10  # Get the next n non-sql answers, 10 by default


class IQueryFlow(Protocol):
    async def start_session(self) -> Response[str]:
        raise NotImplementedError()

    async def stop_session(self, session_id: str) -> Response[None]:
        raise NotImplementedError()

    async def reset_session(self, session_id: str) -> Response[None]:
        raise NotImplementedError()

    async def query(
        self,
        dbId: str,
        session_id: str,
        question: str,
        is_pii_allowed=False,
        with_thoughts: bool = False,
    ) -> Response[str]:
        raise NotImplementedError()

    async def ask(
        self, query_flow_request: QueryFlowRequest
    ) -> Response[AsyncIterator[str]]:
        raise NotImplementedError()


class IQueryFlowListener(Protocol):
    async def on_fail(
        self, session_id: str, db_id: str, question: str, failure_response: Response
    ) -> None:
        raise NotImplementedError()

    async def on_answer(self, query_flow_answer: QueryFlowAnswer) -> None:
        raise NotImplementedError()


class IQueryFlowAnswerRepo(Protocol):
    async def get_query_flow_answers(
        self, request: GetQueryFlowAnswersRequest
    ) -> Response[Sequence[QueryFlowAnswer]]:
        raise NotImplementedError()
