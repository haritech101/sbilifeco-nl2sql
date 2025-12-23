from __future__ import annotations
from typing import Annotated
from sbilifeco.models.base import Response
from fastapi import Request

# Import other required contracts/modules here
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.object_read_update import IObjectReadUpdate
from sbilifeco.cp.object_read_update.paths import Paths


class ObjectReadUpdateHttpServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.object_read_update: IObjectReadUpdate

    def set_object_read_update(
        self, gateway: IObjectReadUpdate
    ) -> ObjectReadUpdateHttpServer:
        self.object_read_update = gateway
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.get(Paths.BY_ID)
        async def read(id: str) -> Response[bytes]:
            try:
                read_response = await self.object_read_update.read(id)
                if not read_response.is_success:
                    return Response.fail(read_response.message, read_response.code)
                elif read_response.payload is None:
                    return Response.fail(f"Object {id} is inexplicably empty", 500)

                return read_response
            except Exception as e:
                return Response.error(e)

        @self.put(Paths.BY_ID)
        async def update(req: Request) -> Response[None]:
            try:
                id = req.path_params.get("id", "")
                content = await req.body()

                update_response = await self.object_read_update.update(id, content)
                if not update_response.is_success:
                    return Response.fail(update_response.message, update_response.code)

                return Response.ok(None)
            except Exception as e:
                return Response.error(e)
