from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from sbilifeco.models.base import Response
from sbilifeco.cp.llm.paths import Paths
from sbilifeco.models.db_metadata import DB
from requests import Request


class LLMHttpClient(HttpClient, ILLM):
    async def add_context(self, context: list[ChatMessage]) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.CONTEXT}",
                    json=[piece.model_dump() for piece in context],
                )
            )
        except Exception as e:
            return Response.error(e)

    async def set_metadata(self, db: DB) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="PUT",
                    url=f"{self.url_base}{Paths.METADATA}",
                    json=db.model_dump(),
                )
            )
        except Exception as e:
            return Response.error(e)

    async def generate_sql(self, question: str) -> Response[str]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.QUERIES}",
                    headers={"Content-Type": "text/plain"},
                    data=question,
                )
            )
        except Exception as e:
            return Response.error(e)
