from __future__ import annotations
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.models.base import Response
from anthropic import AsyncAnthropicVertex


class VertexAI(ILLM):
    def __init__(self) -> None:
        self.vertex_client: AsyncAnthropicVertex
        self.region: str = ""
        self.project_id: str = ""
        self.model: str = ""

    def set_region(self, region: str) -> VertexAI:
        self.region = region
        return self

    def set_project_id(self, project_id: str) -> VertexAI:
        self.project_id = project_id
        return self

    def set_model(self, model: str) -> VertexAI:
        self.model = model
        return self

    async def async_init(self) -> None:
        self.vertex_client = AsyncAnthropicVertex(
            region=self.region, project_id=self.project_id
        )

    async def async_shutdown(self) -> None:
        await self.vertex_client.close()

    async def generate_reply(self, context: str) -> Response[str]:
        try:
            message = await self.vertex_client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": context,
                    }
                ],
                model=self.model,
            )

            return Response.ok(
                "\n".join(
                    [block.text for block in message.content if block.type == "text"]
                )
            )
        except Exception as e:
            return Response.error(e)
