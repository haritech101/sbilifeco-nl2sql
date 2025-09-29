from asyncio import run, sleep
from os import getenv
from typing import NoReturn

from dotenv import load_dotenv
from sbilifeco.cp.llm.http_server import LLMHttpServer
from sbilifeco.gateways.vertex import VertexAI

from envvars import Defaults, EnvVars


class VertexLLMMicroservice:
    async def start(self):
        # Settings from environment
        region = getenv(EnvVars.vertex_ai_region, Defaults.vertex_ai_region)
        project_id = getenv(EnvVars.vertex_ai_project_id, "")
        model = getenv(EnvVars.vertex_ai_model, Defaults.vertex_ai_model)
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        # Vertex gateway
        self.llm = (
            VertexAI().set_region(region).set_project_id(project_id).set_model(model)
        )
        await self.llm.async_init()

        # HTTP server
        self.http_server = LLMHttpServer()
        self.http_server.set_llm(self.llm).set_http_port(http_port)
        await self.http_server.listen()

    async def run_forever(self) -> NoReturn:
        await self.start()
        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(VertexLLMMicroservice().run_forever())
