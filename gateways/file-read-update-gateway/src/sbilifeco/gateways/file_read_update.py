from __future__ import annotations
from typing import Optional
from pprint import pprint, pformat
from os import getenv
from asyncio import run
from dotenv import load_dotenv
from pydantic import BaseModel
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.boundaries.object_read_update import IObjectReadUpdate


class FileReadUpdateGateway(IObjectReadUpdate):
    def __init__(self):
        self.path_map = {}

    def set_path_map(self, path_map: dict[str, str]) -> FileReadUpdateGateway:
        self.path_map = path_map
        return self

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def read(self, object_id: str) -> Response[bytes]:
        try:
            print(f"Find file path for object id {object_id}", flush=True)
            file_path = self.path_map.get(object_id)
            if not file_path:
                print(f"File not found for object id {object_id}", flush=True)
                return Response.fail(f"File not found for object_id: {object_id}", 404)
            print(f"File for {object_id} is {file_path}", flush=True)

            with open(file_path, "rb") as f:
                content = f.read()
            return Response.ok(content)
        except Exception as e:
            return Response.error(e)

    async def update(self, object_id: str, content: bytes) -> Response[None]:
        try:
            print(f"Find file path for object id {object_id}", flush=True)
            file_path = self.path_map.get(object_id)
            if not file_path:
                print(f"File not found for object id {object_id}", flush=True)
                return Response.fail(f"File not found for object_id: {object_id}", 404)
            print(f"File for {object_id} is {file_path}", flush=True)

            with open(file_path, "wb") as f:
                f.write(content)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)
