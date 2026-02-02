from asyncio import run, sleep
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults

# import required modules here
from sbilifeco.flows.non_sql_notify_flow import NonSqlNotifyFlow
from sbilifeco.cp.non_sql_notify_flow.kafka_consumer import NonSqlNotifyTriggerConsumer
from sbilifeco.cp.non_sql_answer_repo.http_client import NonSQLAnswerRepoHttpClient


class NonSQLNotifyMicroservice:
    async def run(self):
        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)
        max_items = int(getenv(EnvVars.max_items, Defaults.max_items))
        repo_proto = getenv(
            EnvVars.non_sql_answer_repo_proto, Defaults.non_sql_answer_repo_proto
        )
        repo_host = getenv(
            EnvVars.non_sql_answer_repo_host, Defaults.non_sql_answer_repo_host
        )
        repo_port = int(
            getenv(EnvVars.non_sql_answer_repo_port, Defaults.non_sql_answer_repo_port)
        )

        print(
            f"Connecting to Non-SQL Answer Repo at {repo_proto}://{repo_host}:{repo_port}"
        )
        self.repo = NonSQLAnswerRepoHttpClient()
        self.repo.set_proto(repo_proto).set_host(repo_host).set_port(repo_port)

        print(
            f"Initialising Non-SQL Notify Flow with capacity of {max_items} items at a time"
        )
        self.flow = (
            NonSqlNotifyFlow()
            .set_non_sql_answer_repo(self.repo)
            .set_max_items(max_items)
        )
        await self.flow.async_init()

        print(f"Initialising Non-SQL Notify Trigger Consumer connecting to {kafka_url}")
        self.consumer = NonSqlNotifyTriggerConsumer().set_flow(self.flow)
        self.consumer.add_host(kafka_url)
        await self.consumer.async_init()

        print("Ready or not, here I come")
        await self.consumer.listen()

    async def run_forever(self):
        await self.run()
        while True:
            await sleep(3600)

    async def stop(self) -> None:
        await self.consumer.stop_consuming()
        await self.consumer.async_shutdown()
        await self.flow.async_shutdown()


if __name__ == "__main__":
    load_dotenv()
    run(NonSQLNotifyMicroservice().run_forever())
