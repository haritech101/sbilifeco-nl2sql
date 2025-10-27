from __future__ import annotations
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.models.base import Response
from google import genai
from google.genai import types, Client
import traceback


class VertexGemini(ILLM):
    def __init__(self) -> None:
        self.vertex_client: Client
        self.region: str = ""
        self.project_id: str = ""
        self.model: str = ""
        self.max_output_tokens = 8192

    def set_region(self, region: str) -> VertexGemini:
        self.region = region
        return self

    def set_project_id(self, project_id: str) -> VertexGemini:
        self.project_id = project_id
        return self

    def set_model(self, model: str) -> VertexGemini:
        self.model = model
        return self

    def set_max_output_tokens(self, max_output_tokens: int) -> VertexGemini:
        self.max_output_tokens = max_output_tokens
        return self

    async def async_init(self) -> None:
        self.vertex_client = Client(
            vertexai=True, location=self.region, project=self.project_id
        )

    async def async_shutdown(self) -> None:
        self.vertex_client.close()

    async def generate_reply(self, context: str) -> Response[str]:
        try:
            llm_response = self.vertex_client.models.generate_content(
                model=self.model,
                contents=context,
                config=types.GenerateContentConfig(temperature=0.0),
            )

            return Response.ok(llm_response.text)
        except Exception as e:
            traceback.print_exc()
            return Response.error(e)
