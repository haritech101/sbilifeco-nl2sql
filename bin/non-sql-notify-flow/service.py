from asyncio import run, sleep
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults

# import required modules here
from sbilifeco.flows.non_sql_notify_flow import NonSqlNotifyFlow
from sbilifeco.cp.non_sql_notify_flow.kafka_consumer import NonSqlNotifyTriggerConsumer
from sbilifeco.cp.non_sql_answer_repo.http_client import NonSQLAnswerRepoHttpClient
from sbilifeco.cp.non_sql_presenter.html_page import NonSqlHtmlPresenter


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
        self.web_page_path = getenv(EnvVars.web_page_path, Defaults.web_page_path)
        template_path = getenv(EnvVars.template_path, Defaults.template_path)

        print(
            f"Connecting to Non-SQL Answer Repo at {repo_proto}://{repo_host}:{repo_port}"
        )
        self.repo = NonSQLAnswerRepoHttpClient()
        self.repo.set_proto(repo_proto).set_host(repo_host).set_port(repo_port)

        print(
            "Initialising Non-SQL Answer HTML Presenter\n"
            f"HTML will be written to {self.web_page_path}\n"
            f"using template at {template_path}"
        )
        self.presenter = NonSqlHtmlPresenter()
        (
            self.presenter.set_web_page_path(self.web_page_path).set_template_path(
                template_path
            )
        )
        await self.presenter.async_init()

        print(
            f"Initialising Non-SQL Notify Flow with capacity of {max_items} items at a time"
        )
        self.flow = (
            NonSqlNotifyFlow()
            .set_non_sql_answer_repo(self.repo)
            .set_max_items(max_items)
        )
        self.flow.add_presenter(self.presenter)
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
