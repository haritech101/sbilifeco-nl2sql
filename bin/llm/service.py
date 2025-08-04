from asyncio import run, sleep
from sbilifeco.gateways.gemini import Gemini
from sbilifeco.cp.llm.microservice import LLMMicroservice
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults


class LLMExecutable:
    async def start(self) -> None:
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        llm_model = getenv(EnvVars.llm_model, Defaults.llm_model)
        api_key = getenv(EnvVars.api_key, None)
        preamble_file = getenv(EnvVars.preamble_file, None)
        postamble_file = getenv(EnvVars.postamble_file, None)

        if not api_key:
            raise ValueError("API_KEY environment variable is required.")

        gemini = Gemini()
        gemini.set_api_key(api_key).set_model(llm_model)

        if preamble_file:
            with open(preamble_file, "r") as file:
                await gemini.set_preamble(file.read())

        if postamble_file:
            with open(postamble_file, "r") as file:
                await gemini.set_postamble(file.read())

        await gemini.async_init()

        microservice = LLMMicroservice()
        microservice.set_llm(gemini).set_http_port(http_port)

        await microservice.listen()

    async def run_forever(self) -> None:
        await self.start()

        while True:
            await sleep(10000)


if __name__ == "__main__":
    run(LLMExecutable().run_forever())
