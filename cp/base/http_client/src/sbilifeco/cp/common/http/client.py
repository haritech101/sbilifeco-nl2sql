from __future__ import annotations
from asyncio import get_event_loop
from typing import Any
from requests import Request, Session
from sbilifeco.models.base import Response


class HttpClient:
    IMPLICIT_PORT = 80

    def set_proto(self, proto: str) -> HttpClient:
        """Set the protocol for the HTTP client."""
        self.proto = proto
        return self

    def set_host(self, host: str) -> HttpClient:
        """Set the host for the HTTP client."""
        self.host = host
        return self

    def set_port(self, port: int) -> HttpClient:
        """Set the port for the HTTP client."""
        self.port = port
        return self

    @property
    def url_base(self) -> str:
        """Construct the URL from the protocol, host, and port."""
        port_section = f":{self.port}" if self.port != self.IMPLICIT_PORT else ""
        return f"{self.proto}://{self.host}{port_section}"

    async def request_as_model(self, req: Request) -> Response[Any]:
        with Session() as session:
            prep_req = session.prepare_request(req)
            http_response = await get_event_loop().run_in_executor(
                None, session.send, prep_req
            )
            if not http_response.ok:
                return Response.fail(
                    message=http_response.content.decode("utf-8"),
                    code=http_response.status_code,
                )

            try:
                return Response.model_validate(http_response.json())
            except Exception as e:
                return Response.error(e)

    async def request_as_binary(self, req: Request) -> Response[bytes]:
        """Send a request and return the response as binary data."""
        with Session() as session:
            prep_req = session.prepare_request(req)
            http_response = await get_event_loop().run_in_executor(
                None, session.send, prep_req
            )
            if not http_response.ok:
                return Response.fail(
                    message=http_response.content.decode("utf-8"),
                    code=http_response.status_code,
                )

            return Response.ok(http_response.content)
