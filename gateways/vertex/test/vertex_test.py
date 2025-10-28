import sys

sys.path.append("./src")

from sbilifeco.gateways.vertex import VertexAI
from sbilifeco.gateways.vertex_gemini import VertexGemini

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from envvars import EnvVars, Defaults

# Import the necessary service(s) here


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        region = getenv(EnvVars.vertex_ai_region, Defaults.vertex_ai_region)
        project_id = getenv(EnvVars.vertex_ai_project_id, "")
        model = getenv(EnvVars.vertex_ai_model, Defaults.vertex_ai_model)

        # Initialise the service(s) here
        self.claude_service = (
            VertexAI().set_region(region).set_project_id(project_id).set_model(model)
        )
        await self.claude_service.async_init()

        self.gemini_service = (
            VertexGemini()
            .set_region(region)
            .set_project_id(project_id)
            .set_model(model)
        )

        await self.gemini_service.async_init()

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.claude_service.async_shutdown()

    async def test_claude(self) -> None:
        response = await self.claude_service.generate_reply(
            "What is the answer to life, the universe and everything?"
        )
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        print(response.payload, flush=True)

    async def test_gemini(self) -> None:
        response = await self.gemini_service.generate_reply(
            "What is the answer to life, the universe and everything?"
        )
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        print(response.payload, flush=True)
