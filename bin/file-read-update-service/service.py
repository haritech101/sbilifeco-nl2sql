from __future__ import annotations
from os import getenv
from pprint import pprint
from asyncio import run, sleep
from dotenv import load_dotenv
from pydantic import BaseModel
from sbilifeco.gateways.file_read_update import FileReadUpdateGateway
from sbilifeco.cp.object_read_update.http_server import ObjectReadUpdateHttpServer
from envvars import EnvVars, Defaults

# Import other required contracts/modules here
from yaml import safe_load


class FileConfig(BaseModel):
    files: dict[str, str]


class FileReadUpdateService:
    def __init__(self):
        self.config_file = ""

    async def run(self, **kwargs) -> None:
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        config_path = getenv(EnvVars.config_path, Defaults.config_path)

        with open(config_path, "r") as f:
            config = safe_load(f)

        self.config = FileConfig.model_validate(config)
        pprint(self.config.model_dump())

        self.file_read_update_gateway = FileReadUpdateGateway()
        (self.file_read_update_gateway.set_path_map(self.config.files))

        self.http_server = ObjectReadUpdateHttpServer()
        (
            self.http_server.set_object_read_update(
                self.file_read_update_gateway
            ).set_http_port(http_port)
        )
        await self.http_server.listen()

    async def run_forever(self) -> None:
        await self.run()
        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(FileReadUpdateService().run_forever())
