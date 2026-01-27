from __future__ import annotations
from typing import Optional, AsyncGenerator
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from aiokafka import AIOKafkaConsumer
from asyncio import create_task, wait_for
from uuid import uuid4


class PubsubConsumer:
    def __init__(self):
        self.hosts: list[str] = []
        self.consumer: AIOKafkaConsumer
        self.subscriptions: list[str] = []
        self.default_timeout: int = 5
        self.should_keep_consuming: bool = True
        self.consumer_name = uuid4().hex

    def add_host(self, host: str) -> PubsubConsumer:
        self.hosts.append(host)
        return self

    def add_subscription(self, topic: str) -> PubsubConsumer:
        topic = topic.replace("/", ".")
        topic = topic.replace(" ", ".")
        topic = topic.lstrip(".")

        self.subscriptions.append(topic)
        return self

    def set_consumer_name(self, consumer_name: str) -> PubsubConsumer:
        self.consumer_name = consumer_name
        return self

    async def subscribe(self, topic: str | None = None) -> None:
        if topic:
            self.add_subscription(topic)

        if self.subscriptions:
            print(f"Subscribing to topics {self.subscriptions}", flush=True)
            self.consumer.subscribe(topics=self.subscriptions)

            assoc_attempts = 3
            while assoc_attempts > 0:
                if self.consumer.assignment():
                    break

                print(
                    f"Waiting for partition assignment for topics {self.subscriptions}",
                    flush=True,
                )
                await self.consumer.getmany(timeout_ms=200)
                assoc_attempts -= 1

            if self.consumer.assignment() == set():
                message = f"No partitions assigned for topics {self.subscriptions}"
                print(
                    message,
                    flush=True,
                )
        else:
            print("No subscriptions yet", flush=True)

    async def async_init(self, **kwargs) -> None:
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=",".join(self.hosts),
            group_id=self.consumer_name,
        )
        await self.consumer.start()

        await self.subscribe()

    async def async_shutdown(self, **kwargs) -> None:
        await self.consumer.stop()

    async def consume(self, timeout: Optional[int] = None) -> Response[str]:
        try:
            print(f"Consuming once from topics {self.subscriptions}", flush=True)
            timeout = timeout or self.default_timeout

            task_to_fetch_one = create_task(self.consumer.getone())
            result = await wait_for(task_to_fetch_one, timeout=timeout)

            # Return the actual message content
            message_content = result.value.decode("utf-8")

            # Commit to Kafka that the message has been processed
            await self.consumer.commit()

            return Response.ok(message_content)

        except TimeoutError:
            print(
                f"Received no data on {self.subscriptions} in {timeout} seconds",
                flush=True,
            )
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def consume_forever(
        self, interval: float = 1.0
    ) -> AsyncGenerator[Response[str]]:
        print(f"Consuming forever from topics {self.subscriptions}", flush=True)
        self.should_keep_consuming = True

        while self.should_keep_consuming:
            try:
                async for msg in self.consumer:
                    message_content = msg.value.decode("utf-8")

                    # Commit to Kafka that the message has been processed
                    await self.consumer.commit()

                    yield Response.ok(message_content)

                    if not self.should_keep_consuming:
                        break
            except Exception as e:
                print(f"Error while consuming message: {e}", flush=True)
                yield Response.error(e)

        yield Response.ok(None)

    async def stop_consuming(self) -> None:
        self.should_keep_consuming = False
