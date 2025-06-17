from asyncio import run, sleep
from json import load
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.cp.query_flow.microservice import QueryFlowMicroservice
from os import getenv
from dotenv import load_dotenv
from envvars import EnvVars, Defaults


async def start() -> None:
    load_dotenv()

    llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
    llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
    llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

    storage_proto = getenv(
        EnvVars.metadata_storage_proto, Defaults.metadata_storage_proto
    )
    storage_host = getenv(EnvVars.metadata_storage_host, Defaults.metadata_storage_host)
    storage_port = int(
        getenv(EnvVars.metadata_storage_port, Defaults.metadata_storage_port)
    )

    flow_port = int(getenv(EnvVars.http_port, Defaults.http_port))

    llm = LLMHttpClient()
    llm.set_proto(llm_proto).set_host(llm_host).set_port(llm_port)

    storage = MetadataStorageHttpClient()
    storage.set_proto(storage_proto).set_host(storage_host).set_port(storage_port)

    flow = QueryFlow()
    flow.set_llm(llm).set_metadata_storage(storage)

    microservice = QueryFlowMicroservice()
    microservice.set_query_flow(flow).set_http_port(flow_port)
    await microservice.listen()

    while True:
        await sleep(10000)


run(start())
