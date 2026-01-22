from typing import Protocol
from sbilifeco.models.base import Response, BaseModel


class NonSqlAnswer(BaseModel):
    session_id: str
    db_id: str
    question: str
    answer: str


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


class IQueryFlowListener(Protocol):
    async def on_fail(
        self, session_id: str, db_id: str, question: str, failure_response: Response
    ) -> None:
        raise NotImplementedError()

    async def on_no_sql(self, non_sql_answer: NonSqlAnswer) -> None:
        raise NotImplementedError()
