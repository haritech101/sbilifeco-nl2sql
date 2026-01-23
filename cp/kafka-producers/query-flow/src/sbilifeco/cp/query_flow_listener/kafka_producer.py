from __future__ import annotations
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.cp.common.kafka.producer import PubsubProducer
from sbilifeco.boundaries.query_flow import IQueryFlowListener, NonSqlAnswer
from sbilifeco.cp.query_flow.paths import Paths, QueryFailure


class QueryFlowEventKafkaProducer(PubsubProducer, IQueryFlowListener):
    def __init__(self):
        super().__init__()

    async def async_init(self, **kwargs) -> None:
        await super().async_init(**kwargs)

    async def async_shutdown(self, **kwargs) -> None:
        await super().async_shutdown(**kwargs)

    async def on_no_sql(self, non_sql_answer: NonSqlAnswer) -> None:
        await self.publish(
            topic=Paths.NON_SQLS.replace("/", ".")[1:],
            content=non_sql_answer.model_dump_json(),
        )

    async def on_fail(
        self, session_id: str, db_id: str, question: str, failure_response: Response
    ) -> None:
        failure = QueryFailure(
            session_id=session_id,
            db_id=db_id,
            question=question,
            response=failure_response,
        )
        await self.publish(
            topic=Paths.FAILURES.replace("/", ".")[1:],
            content=failure.model_dump_json(),
        )
