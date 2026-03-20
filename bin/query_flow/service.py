from asyncio import run, sleep
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from sbilifeco.boundaries.query_flow import QueryFlowAnswer
from sbilifeco.cp.common.mcp.client import MCPClient
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.query_flow.http_server import QueryFlowHttpService
from sbilifeco.cp.query_flow.kafka_producer import QueryFlowEventProducer
from sbilifeco.cp.query_flow_listener.log_directory_presenter import (
    LogDirectoryPresenter,
)
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient
from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient
from sbilifeco.models.base import Response
from sbilifeco.user_flows.query_flow import QueryFlow

from envvars import Defaults, EnvVars


class QueryFlowMicroservice:
    generic_prompt_file: str
    tool_repo: MCPClient
    llm: LLMHttpClient
    storage: MetadataStorageHttpClient
    session_data_manager: SessionDataManagerHttpClient
    vectoriser: VectoriserHttpClient
    vector_repo: VectorRepoHttpClient
    flow: QueryFlow
    http_service: QueryFlowHttpService

    async def run(self) -> None:
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

        mcp_server_url = getenv(EnvVars.mcp_server_url, Defaults.mcp_server_url)

        vectoriser_proto = getenv(EnvVars.vectoriser_proto, Defaults.vectoriser_proto)
        vectoriser_host = getenv(EnvVars.vectoriser_host, Defaults.vectoriser_host)
        vectoriser_port = int(getenv(EnvVars.vectoriser_port, Defaults.vectoriser_port))

        vector_repo_proto = getenv(
            EnvVars.vector_repo_proto, Defaults.vector_repo_proto
        )
        vector_repo_host = getenv(EnvVars.vector_repo_host, Defaults.vector_repo_host)
        vector_repo_port = int(
            getenv(EnvVars.vector_repo_port, Defaults.vector_repo_port)
        )

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
        log_dir = getenv(EnvVars.log_dir, Defaults.log_dir)

        flow_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Set up connection to Tool Repository service, aka MCP
        self.tool_repo = MCPClient()
        self.tool_repo.set_server_url(mcp_server_url)
        await self.tool_repo.async_init()

        # Set up connection to LLM service
        print(
            f"Connecting to LLM gateway at {llm_proto}://{llm_host}:{llm_port}",
            flush=True,
        )
        self.llm = LLMHttpClient()
        self.llm.set_proto(llm_proto).set_host(llm_host).set_port(llm_port)

        # Vectoriser
        vectoriser_proto = getenv(EnvVars.vectoriser_proto, Defaults.vectoriser_proto)
        vectoriser_host = getenv(EnvVars.vectoriser_host, Defaults.vectoriser_host)
        vectoriser_port = int(getenv(EnvVars.vectoriser_port, Defaults.vectoriser_port))
        print(
            f"Connecting to vectoriser at {vectoriser_proto}://{vectoriser_host}:{vectoriser_port}",
            flush=True,
        )
        self.vectoriser = VectoriserHttpClient()
        self.vectoriser.set_proto(vectoriser_proto).set_host(vectoriser_host).set_port(
            vectoriser_port
        )

        # Vector Repo
        vector_repo_proto = getenv(
            EnvVars.vector_repo_proto, Defaults.vector_repo_proto
        )
        vector_repo_host = getenv(EnvVars.vector_repo_host, Defaults.vector_repo_host)
        vector_repo_port = int(
            getenv(EnvVars.vector_repo_port, Defaults.vector_repo_port)
        )
        print(
            f"Connecting to vector repo at {vector_repo_proto}://{vector_repo_host}:{vector_repo_port}",
            flush=True,
        )
        self.vector_repo = VectorRepoHttpClient()
        self.vector_repo.set_proto(vector_repo_proto).set_host(
            vector_repo_host
        ).set_port(vector_repo_port)

        # Set up connection to Metadata Storage service
        print(
            f"Connecting to DB metadata storage at {storage_proto}://{storage_host}:{storage_port}",
            flush=True,
        )
        self.storage = MetadataStorageHttpClient()
        self.storage.set_proto(storage_proto).set_host(storage_host).set_port(
            storage_port
        )

        # Set up connection to Session Data Manager service
        print(
            f"Connecting to session data manager at {session_data_proto}://{session_data_host}:{session_data_port}",
            flush=True,
        )
        self.session_data_manager = SessionDataManagerHttpClient()
        self.session_data_manager.set_proto(session_data_proto).set_host(
            session_data_host
        ).set_port(session_data_port)

        # Set up kafka producer for query flow events
        print(f"Connecting to Kafka at {kafka_url}", flush=True)
        kafka_producer = QueryFlowEventProducer()
        kafka_producer.add_host(kafka_url)
        await kafka_producer.async_init()

        # Set up log directory presenter
        print(f"Setting up logging directory at {log_dir}", flush=True)
        log_directory_presenter = LogDirectoryPresenter().set_log_directory(log_dir)

        # Set up query flow
        print("Configuring flow", flush=True)
        print(
            f"Generic prompt (non-DB specific) prompt will be read from {self.generic_prompt_file}",
            flush=True,
        )
        self.flow = QueryFlow()
        (
            self.flow.set_external_tool_repo(self.tool_repo)
            .set_is_tool_call_enabled(is_tool_call_enabled)
            .set_llm(self.llm)
            .set_vectoriser(self.vectoriser)
            .set_vector_repo(self.vector_repo)
            .set_metadata_storage(self.storage)
            .set_session_data_manager(self.session_data_manager)
            .add_listener(kafka_producer)
            .add_listener(log_directory_presenter)
        )
        self.flow.set_generic_prompt(f"file://{self.generic_prompt_file}")
        self.set_db_specific_prompts()
        await self.flow.async_init()

        # Set up http-based listener for query flow
        print(f"Listening as HTTP service on port {flow_port}", flush=True)
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
