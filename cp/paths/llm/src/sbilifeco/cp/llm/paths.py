from pydantic import BaseModel


class LLMQuery(BaseModel):
    context: str


class Paths:
    BASE = "/api/v1/llm"
    QUERIES = BASE + "/queries"
