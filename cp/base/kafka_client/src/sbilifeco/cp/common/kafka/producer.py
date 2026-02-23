from __future__ import annotations
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from uuid import uuid4
from aiokafka import AIOKafkaProducer


class PubsubProducer:
    def __init__(self):
        self.hosts: list[str] = []
        self.producer: AIOKafkaProducer
        self.identifier: str = uuid4().hex

    def set_identifier(self, identifier: str) -> PubsubProducer:
        self.identifier = identifier
        return self

    def add_host(self, host: str) -> PubsubProducer:
        self.hosts.append(host)
        return self

    async def async_init(self, **kwargs) -> None:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=",".join(self.hosts), client_id=self.identifier
        )
        await self.producer.start()

    async def async_shutdown(self, **kwargs) -> None:
        await self.producer.flush()
        await self.producer.stop()

    async def publish(
        self, topic: str, content: str, right_now: bool = False
    ) -> Response[None]:
        try:
            topic = topic.replace("/", ".")
            topic = topic.replace(" ", ".")
            topic = topic.lstrip(".")

            print(f"Publishing to topic {topic}", flush=True)
            # Wait for the message to be actually sent
            record_metadata = await self.producer.send_and_wait(
                topic, content.encode("utf-8")
            )

            print(
                f"Message queued to topic '{record_metadata.topic}'"
                f" partition '{record_metadata.partition}' offset '{record_metadata.offset}'",
                flush=True,
            )

            if right_now:
                print("Flushing producer messages", flush=True)
                await self.producer.flush()

            return Response.ok(None)
        except Exception as e:
            print(f"Error publishing message: {e}", flush=True)
            return Response.error(e)
