from __future__ import annotations
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.models.base import Response
from sbin.qgen import QGen
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
