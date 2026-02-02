from __future__ import annotations
from typing import Protocol, Sequence

# Import other required contracts/modules here
from sbilifeco.boundaries.query_flow import NonSqlAnswer


class AbstractNonSqlNotifyFlow:
    def __init__(self) -> None:
        self.presenters: list[INonSqlPresenter] = []

    def add_presenter(self, presenter: INonSqlPresenter) -> AbstractNonSqlNotifyFlow:
        """Add a presenter to the flow."""
        self.presenters.append(presenter)
        return self

    async def fetch_and_notify(self) -> None:
        """Fetch non-SQL answers and notify about them."""
        raise NotImplementedError("This method should be overridden by subclasses.")


class INonSqlPresenter(Protocol):
    async def present(self, answers: Sequence[NonSqlAnswer]) -> None:
        """Present the non-SQL response."""
        raise NotImplementedError("This method should be overridden by subclasses.")
