from __future__ import annotations
from json import dumps
from sbilifeco.boundaries.llm import ILLM
from google.genai import Client
from sbilifeco.models.base import Response


class Gemini(ILLM):
    DEFAULT_MODEL = "gemini-1.5-flash"
    RIGID = 0

    def __init__(self):
        self.model: str = self.DEFAULT_MODEL
        self.api_key: str
        self.client: Client

    def set_model(self, model: str) -> Gemini:
        self.model = model
        return self

    def set_api_key(self, api_key: str) -> Gemini:
        self.api_key = api_key
        return self

    async def async_init(self) -> None:
        self.client = Client(api_key=self.api_key)

    async def generate_reply(self, context: str) -> Response[str]:
        try:
            print(context)
            print(f"{len(context)} characters consumed\n")

            gemini_response = self.client.models.generate_content(
                model=self.model,
                contents=context,
                config={
                    "temperature": self.RIGID,
                },
            )
            answer = (gemini_response.text or "").strip()

            return Response.ok(answer)
        except Exception as e:
            return Response.error(e)
