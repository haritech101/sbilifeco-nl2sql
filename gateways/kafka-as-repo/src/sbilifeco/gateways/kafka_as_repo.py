from __future__ import annotations
from typing import Sequence
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.boundaries.query_flow import (
    GetNonSqlAnswersRequest,
    INonSqlAnswerRepo,
    NonSqlAnswer,
)
from sbilifeco.cp.query_flow.paths import Paths
from sbilifeco.cp.common.kafka.consumer import PubsubConsumer


class KafkaAsRepo(INonSqlAnswerRepo):
    def __init__(self):
        self.kafka_url: str
        self.consumer_name: str
        self.consumer: PubsubConsumer

    def set_kafka_url(self, kafka_url: str) -> KafkaAsRepo:
        self.kafka_url = kafka_url
        return self

    def set_consumer_name(self, consumer_name: str) -> KafkaAsRepo:
        self.consumer_name = consumer_name
        return self

    def set_answer_timeout(self, answer_timeout: float) -> KafkaAsRepo:
        self.answer_timeout = answer_timeout
        return self

    async def async_init(self, **kwargs) -> None:
        self.consumer = (
            PubsubConsumer()
            .add_host(self.kafka_url)
            .set_consumer_name(self.consumer_name)
            .add_subscription(Paths.NON_SQLS.replace("/", ".")[1:])
        )
        await self.consumer.async_init()

    async def async_shutdown(self, **kwargs) -> None:
        await self.consumer.async_shutdown()

    async def get_non_sql_answers(
        self, request: GetNonSqlAnswersRequest
    ) -> Response[Sequence[NonSqlAnswer]]:
        try:
            non_sql_answers: list[NonSqlAnswer] = []
            required_num_answers = request.page_size

            while required_num_answers > 0:
                try:
                    output = await self.consumer.consume(
                        timeout=int(self.answer_timeout)
                    )

                    if not output.is_success:
                        print(f"Error consuming message: {output.message}")
                        continue
                    if output.payload is None:
                        print("Output is blank, so we are probably out of data")
                        return Response.ok(non_sql_answers)

                    answer_as_str = output.payload
                    non_sql_answer = NonSqlAnswer.model_validate_json(answer_as_str)
                    non_sql_answers.append(non_sql_answer)

                    required_num_answers -= 1
                except Exception as e:
                    print(f"Error processing non-SQL answer message: {e}")
                    continue

            return Response.ok(non_sql_answers)
        except Exception as e:
            return Response.error(e)
