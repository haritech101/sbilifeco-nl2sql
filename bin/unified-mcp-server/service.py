from asyncio import run, sleep
from typing import NoReturn
from os import getenv
from dotenv import load_dotenv
from envvars import EnvVars, Defaults
from sbilifeco.cp.unified_mcp_server import UnifiedMCPServer
from sbilifeco.cp.population_counter.http_client import PopulationCounterHttpClient


class UnifiedMCPMicroservice:
    async def run(self):
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        population_counter_proto = getenv(
            EnvVars.population_counter_proto, Defaults.population_counter_proto
        )
        population_counter_host = getenv(
            EnvVars.population_counter_host, Defaults.population_counter_host
        )
        population_counter_port = int(
            getenv(EnvVars.population_counter_port, Defaults.population_counter_port)
        )

        self.population_counter = PopulationCounterHttpClient()
        (
            self.population_counter.set_proto(population_counter_proto)
            .set_host(population_counter_host)
            .set_port(population_counter_port)
        )

        self.mcp_server = UnifiedMCPServer()
        (
            self.mcp_server.set_population_counter(
                self.population_counter
            ).set_http_port(http_port)
        )
        await self.mcp_server.async_init()
        await self.mcp_server.listen()

    async def run_forever(self) -> NoReturn:
        await self.run()

        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(UnifiedMCPMicroservice().run_forever())
