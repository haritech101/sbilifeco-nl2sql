from asyncio import run, sleep, get_running_loop
from typing import AsyncGenerator, TextIO
from webbrowser import get
from sbilifeco.cp.common.mcp.client import MCPClient
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.cp.query_flow.http_server import QueryFlowHttpService
from os import getenv
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class QueryFlowMicroservice(FileSystemEventHandler):
    prompts_file: str
    tool_repo: MCPClient
    llm: LLMHttpClient
    storage: MetadataStorageHttpClient
    session_data_manager: SessionDataManagerHttpClient
    flow: QueryFlow
    http_service: QueryFlowHttpService

    async def run(self) -> None:
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

        mcp_server_url = getenv(EnvVars.mcp_server_url, Defaults.mcp_server_url)

        storage_proto = getenv(
            EnvVars.metadata_storage_proto, Defaults.metadata_storage_proto
        )
        storage_host = getenv(
            EnvVars.metadata_storage_host, Defaults.metadata_storage_host
        )
        storage_port = int(
            getenv(EnvVars.metadata_storage_port, Defaults.metadata_storage_port)
        )

        session_data_proto = getenv(
            EnvVars.session_data_proto, Defaults.session_data_proto
        )
        session_data_host = getenv(
            EnvVars.session_data_host, Defaults.session_data_host
        )
        session_data_port = int(
            getenv(EnvVars.session_data_port, Defaults.session_data_port)
        )

        self.prompts_file = getenv(EnvVars.general_prompts_file, "")
        if not self.prompts_file:
            raise ValueError(
                f"Prompts file path is not set in environment variables: {EnvVars.general_prompts_file}"
            )

        flow_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Set up connection to Tool Repository service, aka MCP
        self.tool_repo = MCPClient()
        self.tool_repo.set_server_url(mcp_server_url)
        await self.tool_repo.async_init()

        # Set up connection to LLM service
        self.llm = LLMHttpClient()
        self.llm.set_proto(llm_proto).set_host(llm_host).set_port(llm_port)

        # Set up connection to Metadata Storage service
        self.storage = MetadataStorageHttpClient()
        self.storage.set_proto(storage_proto).set_host(storage_host).set_port(
            storage_port
        )

        # Set up connection to Session Data Manager service
        self.session_data_manager = SessionDataManagerHttpClient()
        self.session_data_manager.set_proto(session_data_proto).set_host(
            session_data_host
        ).set_port(session_data_port)

        # Set up query flow
        self.flow = QueryFlow()
        (
            self.flow.set_tool_repo(self.tool_repo)
            .set_llm(self.llm)
            .set_metadata_storage(self.storage)
            .set_session_data_manager(self.session_data_manager)
        )
        self.set_flow_prompt()

        # Set up http-based listener for query flow
        self.http_service = QueryFlowHttpService()
        self.http_service.set_query_flow(self.flow).set_http_port(flow_port)
        await self.http_service.listen()

        self.observer = Observer()
        self.observer.schedule(self, path=self.prompts_file, recursive=False)
        get_running_loop().run_in_executor(None, self.observer.start)

    async def run_forever(self) -> None:
        await self.run()

        while True:
            await sleep(10000)

    def set_flow_prompt(self) -> None:
        with open(self.prompts_file) as prompts_stream:
            self.flow.set_prompt(prompts_stream.read())

    def on_modified(self, event) -> None:
        if event.src_path == self.prompts_file:
            print(f"Prompts file changed: {event.src_path}", flush=True)
            self.set_flow_prompt()
            print("Prompts reloaded", flush=True)


if __name__ == "__main__":
    load_dotenv()
    run(QueryFlowMicroservice().run_forever())
