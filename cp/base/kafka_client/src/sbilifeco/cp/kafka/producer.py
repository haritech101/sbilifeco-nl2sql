from __future__ import annotations
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from confluent_kafka import Producer


class PubsubProducer:
    def __init__(self):
        self.hosts: list[str] = []
        self.producer: Producer

    def add_host(self, host: str) -> PubsubProducer:
        self.hosts.append(host)
        return self

    async def async_init(self, **kwargs) -> None:
        self.producer = Producer({"bootstrap.servers": ",".join(self.hosts)})
        ...

    async def async_shutdown(self, **kwargs) -> None: ...

    async def publish(self, topic: str, content: str) -> Response[None]:
        def produce_callback(err, msg):
            if err is not None:
                print(f"Failed to deliver message: {err}", flush=True)
            else:
                print(f"Message produced in topic {msg.topic()}", flush=True)

        try:
            topic = topic.replace("/", ".")
            topic = topic.replace(" ", ".")
            topic = topic.lstrip(".")

            print(f"Publishing to topic {topic}", flush=True)
            self.producer.produce(topic, content, callback=produce_callback)
            self.producer.flush()
            self.producer.poll(1)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)
