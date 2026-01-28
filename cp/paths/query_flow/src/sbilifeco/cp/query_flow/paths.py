from pydantic import BaseModel
from sbilifeco.models.base import Response


class Paths:
    BASE = "/api/v1/query-flow"
    SESSIONS = BASE + "/sessions"
    SESSION_BY_ID = BASE + "/sessions/{session_id}"
    SESSION_RESET = SESSION_BY_ID + "/reset"
    QUERIES = SESSION_BY_ID + "/queries"
    NON_SQLS = BASE + "/non-sqls"
    FAILURES = BASE + "/failures"


class QueryRequest(BaseModel):
    db_id: str
    question: str
    is_pii_allowed: bool = False
    with_thoughts: bool = False


class QueryFailure(BaseModel):
    session_id: str
    db_id: str
    question: str
    response: Response
