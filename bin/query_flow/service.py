from asyncio import run, sleep
from sbilifeco.cp.common.mcp.client import MCPClient
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from sbilifeco.models.base import Response
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.boundaries.query_flow import NonSqlAnswer
from sbilifeco.cp.query_flow.http_server import QueryFlowHttpService
from sbilifeco.cp.query_flow.kafka_producer import QueryFlowEventProducer
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from envvars import EnvVars, Defaults


class QueryFlowMicroservice:
    generic_prompt_file: str
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

        self.generic_prompt_file = getenv(EnvVars.general_prompts_file, "")
        if not self.generic_prompt_file:
            raise ValueError(
                f"Prompts file path is not set in environment variables: {EnvVars.general_prompts_file}"
            )

        is_tool_call_enabled = getenv(
            EnvVars.enable_tool_call, Defaults.enable_tool_call
        )
        is_tool_call_enabled = is_tool_call_enabled.lower() in ("true", "1", "yes")

        kafka_url = getenv(EnvVars.kafka_url, Defaults.kafka_url)

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

        # Set up kafka producer for query flow events
        kafka_producer = QueryFlowEventProducer()
        kafka_producer.add_host(kafka_url)
        await kafka_producer.async_init()

        # Set up query flow
        self.flow = QueryFlow()
        (
            self.flow.set_external_tool_repo(self.tool_repo)
            .set_is_tool_call_enabled(is_tool_call_enabled)
            .set_llm(self.llm)
            .set_metadata_storage(self.storage)
            .set_session_data_manager(self.session_data_manager)
            .add_listener(kafka_producer)
        )
        self.flow.set_generic_prompt(f"file://{self.generic_prompt_file}")
        self.set_db_specific_prompts()
        await self.flow.async_init()

        # Set up http-based listener for query flow
        self.http_service = QueryFlowHttpService()
        self.http_service.set_query_flow(self.flow).set_http_port(flow_port)
        await self.http_service.listen()

    async def run_forever(self) -> None:
        await self.run()

        while True:
            await sleep(10000)

    def set_db_specific_prompts(self) -> None:
        db_prompt_template = getenv(EnvVars.db_prompts_file, "")
        if not db_prompt_template:
            print("No DB-specific prompts file template set", flush=True)
            return

        path_components = db_prompt_template.split("{db_id}/")
        if len(path_components) != 2:
            print(
                "DB-specific prompts file template is not valid, missing {db_id}/ placeholder",
                flush=True,
            )
            return

        parent_folder, within_db_path = path_components
        parent_folder = Path(parent_folder)
        print(
            f"Looping inside folder {parent_folder}, to find subpath {within_db_path} in each subfolder",
            flush=True,
        )
        for db_folder in parent_folder.iterdir():
            if not db_folder.is_dir():
                continue
            elif db_folder.name.startswith("."):
                continue

            db_id = db_folder.name
            prompt_file_path = parent_folder / db_id / within_db_path
            if not prompt_file_path.exists():
                print(
                    f"Prompt file for DB ID {db_id} does not exist at {prompt_file_path}, using the catchall prompt",
                    flush=True,
                )
                continue

            self.flow.set_prompt_by_db(db_id, f"file://{prompt_file_path}")
            print(
                f"Assigned DB-specific prompt for DB ID {db_id} from {prompt_file_path}",
                flush=True,
            )


if __name__ == "__main__":
    load_dotenv()
    run(QueryFlowMicroservice().run_forever())
