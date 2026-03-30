from asyncio import run, sleep
from curses import meta
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults

# import required modules here
from sbilifeco.flows.question_suggestion_flow import QuestionSuggestionFlow
from sbilifeco.cp.question_suggestion_flow.http_server import (
    QuestionSuggestionHttpServer,
)
from sbilifeco.cp.question_suggestion_flow.http_client import (
    QuestionSuggestionHttpClient,
)
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.llm.http_client import LLMHttpClient


class QuestionSuggestionMicroservice:
    async def run(self):
        # env vars
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        metadata_storage_proto = getenv(
            EnvVars.metadata_storage_proto, Defaults.metadata_storage_proto
        )
        metadata_storage_host = getenv(
            EnvVars.metadata_storage_host, Defaults.metadata_storage_host
        )
        metadata_storage_port = int(
            getenv(EnvVars.metadata_storage_port, Defaults.metadata_storage_port)
        )

        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

        prompt_file = getenv(EnvVars.prompt_file, Defaults.prompt_file)

        # services
        self.metadata_storage = MetadataStorageHttpClient()
        (
            self.metadata_storage.set_proto(metadata_storage_proto)
            .set_host(metadata_storage_host)
            .set_port(metadata_storage_port)
        )

        self.llm = LLMHttpClient()
        self.llm.set_proto(llm_proto).set_host(llm_host).set_port(llm_port)

        self.flow = QuestionSuggestionFlow()
        (
            self.flow.set_metadata_storage(self.metadata_storage)
            .set_llm(self.llm)
            .set_prompt_file(prompt_file)
        )
        await self.flow.async_init()

        self.http_server = (
            QuestionSuggestionHttpServer()
            .set_question_suggestion_flow(self.flow)
            .set_http_port(http_port)
        )

        # listen
        await self.http_server.listen()

    async def run_forever(self):
        await self.run()
        while True:
            await sleep(3600)

    async def stop(self): ...


if __name__ == "__main__":
    load_dotenv()
    run(QuestionSuggestionMicroservice().run_forever())
