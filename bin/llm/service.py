from asyncio import run, sleep
from sbilifeco.gateways.gemini import Gemini
from sbilifeco.cp.llm.http_server import LLMHttpServer
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults


class LLMMicroservice:
    async def start(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        llm_model = getenv(EnvVars.llm_model, Defaults.llm_model)
        api_key = getenv(EnvVars.api_key, None)
        thinking_budget = int(getenv(EnvVars.thinking_budget, Defaults.thinking_budget))

        if not api_key:
            raise ValueError("API_KEY environment variable is required.")

        gemini = Gemini()
        gemini.set_api_key(api_key).set_model(llm_model).set_thinking_budget(
            thinking_budget
        )

        await gemini.async_init()

        microservice = LLMHttpServer()
        microservice.set_llm(gemini).set_http_port(http_port)

        await microservice.listen()

    async def run_forever(self) -> None:
        await self.start()

        while True:
            await sleep(10000)


if __name__ == "__main__":
    run(LLMMicroservice().run_forever())
