from __future__ import annotations

from pprint import pprint

# Import other required contracts/modules here
from sbilifeco.boundaries.non_sql_notify_flow import AbstractNonSqlNotifyFlow
from sbilifeco.boundaries.query_flow import (
    GetNonSqlAnswersRequest,
    INonSqlAnswerRepo,
)


class NonSqlNotifyFlow(AbstractNonSqlNotifyFlow):
    def __init__(self):
        super().__init__()
        self.repo: INonSqlAnswerRepo
        self.max_items = 10

    def set_non_sql_answer_repo(self, repo: INonSqlAnswerRepo) -> NonSqlNotifyFlow:
        self.repo = repo
        return self

    def set_max_items(self, max_items: int) -> NonSqlNotifyFlow:
        self.max_items = max_items
        return self

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def fetch_and_notify(self) -> None:
        try:
            print("Fetching the latest non-SQL answers", flush=True)
            request = GetNonSqlAnswersRequest(page_size=self.max_items)

            response = await self.repo.get_non_sql_answers(request)
            if not response.is_success:
                print(
                    f"Error fetching non-SQL answers from repo: {response.message}",
                    flush=True,
                )
                return
            elif response.payload is None:
                print("List of non-SQL is corrupted", flush=True)
                return
            non_sql_answers = response.payload

            print(
                f"Invoking {len(self.presenters)} configured presenters to notify about non-SQL answers",
                flush=True,
            )
            for presenter in self.presenters:
                await presenter.present(non_sql_answers)
        except Exception as e:
            pprint(f"Error in fetch_and_notify: {e}")
            raise e
