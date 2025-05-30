from asyncio import run, sleep
from sbilifeco.gateways.ollama import Ollama
from sbilifeco.cp.llm.microservice import LLMMicroservice
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults


async def start():
    load_dotenv()

    http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
    llm_model = getenv(EnvVars.llm_model, Defaults.llm_model)

    ollama = Ollama()
    ollama.set_host("localhost").set_model(llm_model)
    await ollama.async_init()

    microservice = LLMMicroservice()
    microservice.set_llm(ollama).set_http_port(http_port)

    await microservice.listen()

    while True:
        await sleep(10000)


run(start())
