from asyncio import run, sleep
from sbilifeco.gateways.gemini import Gemini
from sbilifeco.cp.llm.microservice import LLMMicroservice
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults


async def start():
    load_dotenv()

    http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
    llm_model = getenv(EnvVars.llm_model, Defaults.llm_model)
    api_key = getenv(EnvVars.api_key, None)

    if not api_key:
        raise ValueError("API_KEY environment variable is required.")

    gemini = Gemini()
    gemini.set_api_key(api_key).set_model(llm_model)
    await gemini.async_init()

    microservice = LLMMicroservice()
    microservice.set_llm(gemini).set_http_port(http_port)

    await microservice.listen()

    while True:
        await sleep(10000)


run(start())
