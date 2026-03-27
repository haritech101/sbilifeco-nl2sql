from __future__ import annotations
from typing import Protocol, AsyncIterator, Sequence
from sbilifeco.models.base import Response, BaseModel


# Import other required contracts/modules here


class QuestionSuggestionRequest(BaseModel):
    db_id: str
    num_suggestions_per_batch: int = 5
    interval_in_seconds: int = 5


class SuggestedQuestion(BaseModel):
    question: str


class IQuestionSuggestionFlow(Protocol):
    async def suggest(
        self, req: QuestionSuggestionRequest
    ) -> Response[AsyncIterator[Sequence[SuggestedQuestion]]]: ...
