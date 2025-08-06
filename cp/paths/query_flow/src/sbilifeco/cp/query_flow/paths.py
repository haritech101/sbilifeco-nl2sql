from pydantic import BaseModel


class Paths:
    BASE = "/api/v1/query-flow"
    SESSIONS = BASE + "/sessions"
    SESSION_BY_ID = BASE + "/sessions/{session_id}"
    SESSION_RESET = SESSION_BY_ID + "/reset"
    QUERIES = SESSION_BY_ID + "/queries"


class QueryRequest(BaseModel):
    db_id: str
    question: str
