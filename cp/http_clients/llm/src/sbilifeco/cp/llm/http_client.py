from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from sbilifeco.models.base import Response
from sbilifeco.cp.llm.paths import Paths, LLMQuery
from requests import Request


class LLMHttpClient(HttpClient, ILLM):
    async def generate_reply(self, context: str) -> Response[str]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.QUERIES}",
                    json=LLMQuery(context=context).model_dump(),
                )
            )
        except Exception as e:
            return Response.error(e)
