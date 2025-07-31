from pydantic import BaseModel


class Paths:
    BASE = "/api/v1/query-flow"
    QUERIES = BASE + "/queries"
    RESET = BASE + "/reset-requests"


class QueryRequest(BaseModel):
    db_id: str
    question: str
