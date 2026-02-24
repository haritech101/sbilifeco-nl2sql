from __future__ import annotations
from typing import Protocol, Sequence

# Import other required contracts/modules here
from sbilifeco.boundaries.query_flow import QueryFlowAnswer


class AbstractAnswerNotifyFlow:
    def __init__(self) -> None:
        self.presenters: list[IAnswerPresenter] = []

    def add_presenter(self, presenter: IAnswerPresenter) -> AbstractAnswerNotifyFlow:
        """Add a presenter to the flow."""
        self.presenters.append(presenter)
        return self

    async def fetch_and_notify(self) -> None:
        """Fetch answers and notify about them."""
        raise NotImplementedError("This method should be overridden by subclasses.")


class IAnswerPresenter(Protocol):
    async def present(self, answers: Sequence[QueryFlowAnswer]) -> None:
        """Present the answers."""
        raise NotImplementedError("This method should be overridden by subclasses.")
