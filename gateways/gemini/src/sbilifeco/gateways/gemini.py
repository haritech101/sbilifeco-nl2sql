from __future__ import annotations
from sbilifeco.boundaries.llm import ILLM
from google.genai import Client
from google.genai.types import GenerateContentConfig, ThinkingConfig
from sbilifeco.models.base import Response


class Gemini(ILLM):
    DEFAULT_MODEL = "gemini-1.5-flash"
    RIGID = 0
    DYNAMIC_BUDGET = -1
    NO_BUDGET = 0

    def __init__(self):
        self.model: str = self.DEFAULT_MODEL
        self.api_key: str
        self.thinking_budget: int = self.DYNAMIC_BUDGET
        self.client: Client

    def set_model(self, model: str) -> Gemini:
        self.model = model
        return self

    def set_api_key(self, api_key: str) -> Gemini:
        self.api_key = api_key
        return self

    def set_thinking_budget(self, budget: int) -> Gemini:
        self.thinking_budget = budget
        return self

    async def async_init(self) -> None:
        self.client = Client(api_key=self.api_key)

    async def generate_reply(self, context: str) -> Response[str]:
        try:
            print(context)
            print(f"{len(context)} characters consumed\n")

            config = GenerateContentConfig(
                temperature=self.RIGID,
                thinking_config=ThinkingConfig(thinking_budget=self.thinking_budget),
            )

            gemini_response = self.client.models.generate_content(
                model=self.model,
                contents=context,
                config=config,
            )
            answer = (gemini_response.text or "").strip()

            return Response.ok(answer)
        except Exception as e:
            return Response.error(e)
