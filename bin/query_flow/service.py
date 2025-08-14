from asyncio import run, sleep
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.session_data_manager.http_client import SessionDataManagerHttpClient
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.cp.query_flow.http_server import QueryFlowHttpService
from os import getenv
from dotenv import load_dotenv
from envvars import EnvVars, Defaults


class QueryFlowMicroservice:
    async def run(self) -> None:
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

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

        preamble = ""
        preamble_file = getenv(EnvVars.preamble_file)
        if preamble_file:
            with open(preamble_file) as preamble_stream:
                preamble = preamble_stream.read()

        postamble = ""
        postamble_file = getenv(EnvVars.postamble_file)
        if postamble_file:
            with open(postamble_file) as postamble_stream:
                postamble = postamble_stream.read()

        flow_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        llm = LLMHttpClient()
        llm.set_proto(llm_proto).set_host(llm_host).set_port(llm_port)

        storage = MetadataStorageHttpClient()
        storage.set_proto(storage_proto).set_host(storage_host).set_port(storage_port)

        session_data_manager = SessionDataManagerHttpClient()
        session_data_manager.set_proto(session_data_proto).set_host(
            session_data_host
        ).set_port(session_data_port)

        flow = QueryFlow()
        flow.set_llm(llm).set_metadata_storage(storage).set_session_data_manager(
            session_data_manager
        ).set_preamble(preamble).set_postamble(postamble)

        microservice = QueryFlowHttpService()
        microservice.set_query_flow(flow).set_http_port(flow_port)
        await microservice.listen()

    async def run_forever(self) -> None:
        await self.run()

        while True:
            await sleep(10000)


if __name__ == "__main__":
    load_dotenv()
    run(QueryFlowMicroservice().run_forever())
