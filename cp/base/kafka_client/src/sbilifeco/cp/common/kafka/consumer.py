from __future__ import annotations
from typing import Optional, AsyncGenerator
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from confluent_kafka import Consumer, KafkaError
from functools import partial
from asyncio import to_thread


class PubsubConsumer:
    def __init__(self):
        self.hosts: list[str] = []
        self.consumer: Consumer
        self.subscriptions: list[str] = []
        self.default_timeout: int = 5
        self.should_keep_consuming: bool = True

    def add_host(self, host: str) -> PubsubConsumer:
        self.hosts.append(host)
        return self

    def add_subscription(self, topic: str) -> PubsubConsumer:
        topic = topic.replace("/", ".")
        topic = topic.replace(" ", ".")
        topic = topic.lstrip(".")

        self.subscriptions.append(topic)
        return self

    async def subscribe(self, topic: str | None = None) -> None:
        if topic:
            self.add_subscription(topic)
        if self.subscriptions:
            self.consumer.subscribe(topics=self.subscriptions)

    async def async_init(self, **kwargs) -> None:
        self.consumer = Consumer(
            {
                "bootstrap.servers": ",".join(self.hosts),
                "group.id": "tech101-consumer-group",
                "auto.offset.reset": "earliest",
            }
        )
        await self.subscribe()

    async def async_shutdown(self, **kwargs) -> None:
        self.consumer.close()

    async def consume(self, timeout: Optional[int] = None) -> Response[str]:
        try:
            print(f"Consuming from topics {self.subscriptions}", flush=True)
            timeout = timeout or self.default_timeout
            result = await to_thread(self.consumer.poll, timeout=timeout)

            if result is None:
                return Response.ok(None)

            err = result.error()
            if err is not None:
                if err.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(
                        f"One or more of topics {self.subscriptions} do not exist yet."
                    )
                    return Response.ok(None)
                return Response.fail(f"Consumer error: {err}")

            result_payload = result.value()
            if result_payload is None:
                return Response.ok(None)

            return Response.ok(result_payload.decode())
        except Exception as e:
            return Response.error(e)

    async def consume_forever(
        self, interval: float = 1.0
    ) -> AsyncGenerator[Response[str]]:
        print(f"Consuming forever from topics {self.subscriptions}", flush=True)
        self.should_keep_consuming = True

        while self.should_keep_consuming:
            try:
                result = await to_thread(partial(self.consumer.poll, timeout=interval))

                if result is None:
                    yield Response.ok(None)
                    continue

                err = result.error()
                if err is not None:
                    if err.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        print(
                            f"One or more of topics {self.subscriptions} do not exist yet."
                        )
                        yield Response.ok(None)
                        continue

                    yield Response.fail(f"Consumer error: {err}")
                    continue

                result_payload = result.value()
                if result_payload is None:
                    yield Response.ok(None)
                    continue

                print(f"Message consumed from topics {result.topic()}", flush=True)
                yield Response.ok(result_payload.decode())
            except Exception as e:
                print(f"Error while consuming: {e}", flush=True)
                yield Response.error(e)

        yield Response.ok(None)

    async def stop_consuming(self) -> None:
        self.should_keep_consuming = False
