from __future__ import annotations
import asyncio
from os import getenv
from dotenv import load_dotenv
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.models.base import Response
from sbin.qgen import QGen
from sbin.envvars import EnvVars, Defaults
from requests import Request


class Paths:
    generate_requests = "/generate-requests"


class QGenHttpServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.qgen: QGen

    def set_qgen(self, qgen: QGen) -> QGenHttpServer:
        self.qgen = qgen
        return self

    async def listen(self) -> None:
        return await super().listen()

    async def stop(self) -> None:
        return await super().stop()

    async def run(self) -> None:
        conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))
        http_listen_port = int(
            getenv(EnvVars.http_listen_port, Defaults.http_listen_port)
        )

        service = (
            QGen()
            .set_conn_string(conn_string)
            .set_llm_scheme(llm_proto, llm_host, llm_port)
        )

        await service.async_init()

        try:
            self.set_qgen(service)
            self.set_http_port(http_listen_port)
            await self.listen()
            print("HTTP server started")
        finally:
            await service.async_shutdown()

    async def run_forever(self) -> None:
        await self.run()

        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            await self.stop()

    def build_routes(self) -> None:
        super().build_routes()

        @self.get(Paths.generate_requests)
        async def generate_requests(num_requests: int = -1) -> Response[str]:
            try:
                return Response.ok(await self.qgen.generate_with_llm(num_requests))
            except Exception as e:
                return Response.error(e)


class QGenHttpClient(HttpClient):
    async def generate_requests(self, num_requests: int = -1) -> Response[str]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.generate_requests}",
                params={"num_requests": num_requests},
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(QGenHttpServer().run_forever())
