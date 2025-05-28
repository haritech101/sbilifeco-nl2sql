from asyncio import run, sleep
from dotenv import load_dotenv
from sbilifeco.gateways.fs_metadata_storage import FSMetadataStorage
from sbilifeco.cp.metadata_storage.microservice import MetadataStorageMicroservice
from envvars import EnvVars, Defaults
from os import getenv


async def start():
    load_dotenv()

    http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
    metadata_path = getenv(EnvVars.metadata_path, Defaults.metadata_path)

    storage = FSMetadataStorage().set_metadata_path(metadata_path)
    microservice = MetadataStorageMicroservice().set_metadata_storage(storage)
    microservice.set_http_port(http_port)
    await microservice.start()

    while True:
        await sleep(10000)


run(start())
