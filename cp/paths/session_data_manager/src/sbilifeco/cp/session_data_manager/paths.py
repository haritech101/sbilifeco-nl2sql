from pydantic import BaseModel


class Paths:
    BASE = "/api/v1/session-data"
    SESSION_DATA_BY_ID = BASE + "/{session_id}"


class SessionData(BaseModel):
    data: str
