from asyncio import run, sleep
from dotenv import load_dotenv
from sbilifeco.gateways.synmetrix import Synmetrix
from sbilifeco.cp.metadata_storage.microservice import MetadataStorageMicroservice
from envvars import EnvVars, Defaults
from os import getenv


class MetadataStorageExecutable:
    async def start(self):
        load_dotenv()

        db_host = getenv(EnvVars.db_host, Defaults.db_host)
        db_port = int(getenv(EnvVars.db_port, Defaults.db_port))
        db_username = getenv(EnvVars.db_username, Defaults.db_username)
        db_password = getenv(EnvVars.db_password, Defaults.db_password)
        db_name = getenv(EnvVars.db_name, Defaults.db_name)
        print(f"Database details: {db_host}:{db_port}, {db_username}, {db_name}")

        auth_proto = getenv(EnvVars.auth_proto, Defaults.auth_proto)
        auth_host = getenv(EnvVars.auth_host, Defaults.auth_host)
        auth_port = int(getenv(EnvVars.auth_port, Defaults.auth_port))
        auth_username = getenv(EnvVars.auth_username, Defaults.auth_username)
        auth_password = getenv(EnvVars.auth_password, Defaults.auth_password)
        auth_path = getenv(EnvVars.auth_path, Defaults.auth_path)
        print(f"Auth details: {auth_proto}://{auth_host}:{auth_port}, {auth_username}")

        cube_proto = getenv(EnvVars.cube_proto, Defaults.cube_proto)
        cube_host = getenv(EnvVars.cube_host, Defaults.cube_host)
        cube_port = int(getenv(EnvVars.cube_port, Defaults.cube_port))
        print(f"Cube details: {cube_proto}://{cube_host}:{cube_port}")

        gateway = Synmetrix()
        (
            gateway.set_db_host(db_host)
            .set_db_port(db_port)
            .set_db_username(db_username)
            .set_db_password(db_password)
            .set_db_name(db_name)
            .set_auth_proto(auth_proto)
            .set_auth_host(auth_host)
            .set_auth_port(auth_port)
            .set_auth_username(auth_username)
            .set_auth_password(auth_password)
            .set_auth_path(auth_path)
            .set_cube_api_proto(cube_proto)
            .set_cube_api_host(cube_host)
            .set_cube_api_port(cube_port)
        )

        microservice_port = int(
            getenv(EnvVars.microservice_port, Defaults.microservice_port)
        )

        microservice = MetadataStorageMicroservice()
        microservice.set_metadata_storage(gateway).set_http_port(microservice_port)

        await microservice.start()

    async def run_forever(self):
        await self.start()
        while True:
            await sleep(10000)


if __name__ == "__main__":
    run(MetadataStorageExecutable().run_forever())
