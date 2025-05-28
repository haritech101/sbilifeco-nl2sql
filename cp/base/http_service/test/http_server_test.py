import sys
from asyncio import get_event_loop

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase

from requests import Request, Session

from sbilifeco.cp.common.http.server import HttpServer
from fastapi.responses import PlainTextResponse


class ImplHttpServer(HttpServer):
    def build_routes(self):
        @self.get("/")
        async def root() -> PlainTextResponse:
            return PlainTextResponse("Hello, World!")


class HttpServerTest(IsolatedAsyncioTestCase):
    HTTP_PORT = 8181

    async def asyncSetUp(self) -> None:
        self.http_server = ImplHttpServer().set_http_port(self.HTTP_PORT)
        await self.http_server.listen()

    async def asyncTearDown(self) -> None:
        await self.http_server.stop()

    async def test_http_request(self):
        req = Request(
            url=f"http://localhost:{self.HTTP_PORT}/",
            method="GET",
        )
        prep_req = req.prepare()
        session = Session()
        http_response = await get_event_loop().run_in_executor(
            None,
            session.send,
            prep_req,
        )

        self.assertTrue(http_response.ok, http_response.content.decode())

        text = http_response.content.decode()
        self.assertEqual(text, "Hello, World!")
