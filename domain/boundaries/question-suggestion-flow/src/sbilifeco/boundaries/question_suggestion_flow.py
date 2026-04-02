from __future__ import annotations
from typing import Protocol, AsyncIterator, Sequence
from sbilifeco.models.base import Response, BaseModel


# Import other required contracts/modules here


class QuestionSuggestionRequest(BaseModel):
    db_id: str
    """The ID of the database for which to suggest questions."""

    num_suggestions_per_batch: int = 5
    """The number of question suggestions to generate per batch."""

    interval_in_seconds: int = 5
    """The interval in seconds between each batch of question suggestions."""

    randomness: float = 1.0
    """A value between 0 and 1. Higher values will result in more random suggestions, while lower values will result in more deterministic suggestions."""


class SuggestedQuestion(BaseModel):
    question: str


class IQuestionSuggestionFlow(Protocol):
    async def suggest(
        self, req: QuestionSuggestionRequest
    ) -> Response[AsyncIterator[Sequence[SuggestedQuestion]]]: ...
