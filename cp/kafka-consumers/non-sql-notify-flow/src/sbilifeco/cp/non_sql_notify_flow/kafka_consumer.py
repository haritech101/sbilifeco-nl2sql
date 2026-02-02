from __future__ import annotations
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.boundaries.non_sql_notify_flow import AbstractNonSqlNotifyFlow
from sbilifeco.cp.common.kafka.consumer import PubsubConsumer
from sbilifeco.cp.non_sql_notify_flow.paths import Paths


class NonSqlNotifyTriggerConsumer(PubsubConsumer):
    def __init__(self):
        super().__init__()
        self.set_consumer_name("non-sql-notify-trigger-consumer")
        self.add_subscription(Paths.BASE.replace("/", ".").lstrip("."))
        self.flow: AbstractNonSqlNotifyFlow

    def set_flow(self, flow: AbstractNonSqlNotifyFlow) -> NonSqlNotifyTriggerConsumer:
        self.flow = flow
        return self

    async def consume(self, timeout: int | None = None) -> Response[str]:
        try:
            consume_response = await super().consume(timeout=timeout)
            if not consume_response.is_success:
                print(f"Error while consuming from stream: {consume_response.message}")
                return Response.ok(None)
            elif consume_response.payload is None:
                return Response.ok(None)

            print("Received trigger, invoking flow")
            await self.flow.fetch_and_notify()
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def listen(self) -> None:
        try:
            async for consume_response in self.consume_forever():
                if not consume_response.is_success:
                    print(
                        f"Error while consuming from stream: {consume_response.message}"
                    )
                    continue
                elif consume_response.payload is None:
                    continue

                print("Received trigger, invoking flow")
                await self.flow.fetch_and_notify()
        except Exception as e:
            print(f"Error in listen loop: {str(e)}")
