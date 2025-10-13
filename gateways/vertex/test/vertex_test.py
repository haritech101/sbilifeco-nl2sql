import sys

sys.path.append("./src")

from sbilifeco.gateways.vertex import VertexAI

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
        self.service = (
            VertexAI().set_region(region).set_project_id(project_id).set_model(model)
        )
        await self.service.async_init()

        # Initialise the client(s) here

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()

    async def test_ask(self) -> None:
        response = await self.service.generate_reply(
            "What is the answer to life, the universe and everything?"
        )
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        print(response.payload, flush=True)
