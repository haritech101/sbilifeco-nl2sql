from asyncio import run, sleep
from dotenv import load_dotenv
from sbilifeco.gateways.synmetrix import Synmetrix
from sbilifeco.cp.metadata_storage.microservice import MetadataStorageMicroservice
from envvars import EnvVars, Defaults
from os import getenv


async def start():
    load_dotenv()

    db_host = getenv(EnvVars.db_host, Defaults.db_host)
    db_port = int(getenv(EnvVars.db_port, Defaults.db_port))
    db_username = getenv(EnvVars.db_username, Defaults.db_username)
    db_password = getenv(EnvVars.db_password, Defaults.db_password)
    db_name = getenv(EnvVars.db_name, Defaults.db_name)
    auth_port = int(getenv(EnvVars.auth_port, Defaults.auth_port))
    auth_username = getenv(EnvVars.auth_username, Defaults.auth_username)
    auth_password = getenv(EnvVars.auth_password, Defaults.auth_password)
    auth_path = getenv(EnvVars.auth_path, Defaults.auth_path)
    cube_port = int(getenv(EnvVars.cube_port, Defaults.cube_port))

    gateway = Synmetrix()
    (
        gateway.set_db_host(db_host)
        .set_db_port(db_port)
        .set_db_username(db_username)
        .set_db_password(db_password)
        .set_db_name(db_name)
        .set_auth_port(auth_port)
        .set_auth_username(auth_username)
        .set_auth_password(auth_password)
        .set_auth_path(auth_path)
        .set_cube_api_port(cube_port)
    )

    microservice_port = int(
        getenv(EnvVars.microservice_port, Defaults.microservice_port)
    )

    microservice = MetadataStorageMicroservice()
    microservice.set_metadata_storage(gateway).set_http_port(microservice_port)

    await microservice.start()

    while True:
        await sleep(10000)


run(start())
