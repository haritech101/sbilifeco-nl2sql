from __future__ import annotations
from traceback import format_exc
from datetime import date, datetime

# Import other required contracts/modules here
from pathlib import Path

from sbilifeco.boundaries.query_flow import IQueryFlowListener, QueryFlowAnswer
from sbilifeco.models.base import Response
from csv import writer


class LogDirectoryPresenter(IQueryFlowListener):
    def __init__(self):
        self.log_directory = ""

    def set_log_directory(self, log_directory: str) -> LogDirectoryPresenter:
        self.log_directory = log_directory
        return self

    async def async_init(self, **kwargs) -> None: ...

    async def async_shutdown(self, **kwargs) -> None: ...

    async def on_answer(self, query_flow_answer: QueryFlowAnswer) -> None:
        print("Answer received from query flow", flush=True)
        try:
            file_name = f"{date.today().isoformat()}.csv"
            absolute_path = (Path(self.log_directory) / file_name).absolute()
            print(f"Logging answer to {absolute_path}", flush=True)

            with open(absolute_path, "a") as f:
                csv_writer = writer(f)
                csv_writer.writerow(
                    [
                        datetime.now().isoformat(),
                        query_flow_answer.db_id,
                        query_flow_answer.question,
                        query_flow_answer.answer,
                        query_flow_answer.response_time_seconds,
                    ]
                )
                f.flush()
        except Exception as e:
            print(
                f"Error while writing answer to log directory '{self.log_directory}': {e}",
                flush=True,
            )
            print(format_exc(), flush=True)

    async def on_fail(
        self, session_id: str, db_id: str, question: str, failure_response: Response
    ) -> None: ...
