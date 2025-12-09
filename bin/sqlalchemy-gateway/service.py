from asyncio import run, sleep
from os import getenv

from dotenv import load_dotenv
from sbilifeco.gateways.sqlalchemy_gateway import SQLAlchemyGateway
from sbilifeco.cp.metadata_storage.http_server import MetadataStorageHttpServer
from envvars import EnvVars, Defaults


class SQLAlchemyGatewayService:
    async def run(self) -> None:
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        definitions_path = getenv(EnvVars.definitions_path, "")

        self.gateway = SQLAlchemyGateway()
        self.gateway.set_definitions_path(definitions_path)
        await self.gateway.async_init()

        self.http_server = MetadataStorageHttpServer()
        self.http_server.set_metadata_storage(self.gateway).set_http_port(http_port)
        await self.http_server.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(1)


if __name__ == "__main__":
    load_dotenv()
    run(SQLAlchemyGatewayService().run_forever())
