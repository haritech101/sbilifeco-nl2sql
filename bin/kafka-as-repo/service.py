from asyncio import run, sleep
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults

# import required modules here
from sbilifeco.cp.non_sql_answer_repo.http_server import NonSQLAnswerRepoHTTPServer
from sbilifeco.gateways.kafka_as_repo import KafkaAsRepo


class KafkaAsRepoMicroservice:
    async def run(self):
        try:
            # env vars
            http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
            kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
            consumer_name = getenv(
                EnvVars.kafka_consumer_name, Defaults.kafka_consumer_name
            )
            answer_timeout = int(
                getenv(EnvVars.answer_timeout, Defaults.answer_timeout)
            )

            # initiate services
            self.repo = KafkaAsRepo()
            (
                self.repo.set_kafka_url(kafka_url)
                .set_consumer_name(consumer_name)
                .set_answer_timeout(answer_timeout)
            )
            await self.repo.async_init()

            # initiate controllers/presenters
            self.http_server = NonSQLAnswerRepoHTTPServer()
            (self.http_server.set_repo(self.repo).set_http_port(http_port))
            await self.http_server.listen()
        except InterruptedError | KeyboardInterrupt:
            # stop services
            await self.repo.async_shutdown()
            await self.http_server.stop()

    async def run_forever(self):
        await self.run()
        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(KafkaAsRepoMicroservice().run_forever())
