from __future__ import annotations
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.boundaries.object_read_update import IObjectReadUpdate
from sbilifeco.cp.object_read_update.paths import Paths


class ObjectReadUpdateHttpClient(HttpClient, IObjectReadUpdate):
    def __init__(self):
        HttpClient.__init__(self)
        self.proto = "http"
        self.host = "localhost"
        self.port = 80

    async def read(self, object_id: str) -> Response[bytes]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.BY_ID.format(id=object_id)}"
            req = Request(url=url, method="GET")

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            if res.payload and not isinstance(res.payload, bytes):
                if isinstance(res.payload, str):
                    res.payload = res.payload.encode("utf-8")
                else:
                    res.payload = bytes(res.payload)

            # Return response
            return res
        except Exception as e:
            return Response.error(e)

    async def update(self, object_id: str, content: bytes) -> Response[None]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.BY_ID.format(id=object_id)}"
            req = Request(
                url=url,
                method="PUT",
                headers={"Content-Type": "application/octet-stream"},
                data=content,
            )

            # Send request
            res = await self.request_as_model(req)

            # Triage response
            ...

            # Return response
            return res
        except Exception as e:
            return Response.error(e)
