from asyncio import run, sleep
from os import getenv
from dotenv import load_dotenv
from sbilifeco.gateways.redis import Redis
from sbilifeco.cp.session_data_manager.http_server import SessionDataManagerHttpServer
from sbilifeco.cp.population_counter.http_server import PopulationCounterHttpServer
from envvars import EnvVars, Defaults


class SessionDataManagerMicroservice:
    async def run(self):
        redis_host = getenv(EnvVars.redis_host, Defaults.redis_host)
        redis_port = int(getenv(EnvVars.redis_port, Defaults.redis_port))
        redis_db = int(getenv(EnvVars.redis_db, Defaults.redis_db))
        http_port_session_data = int(
            getenv(EnvVars.http_port_session_data, Defaults.http_port_session_data)
        )
        http_port_population = int(
            getenv(EnvVars.http_port_population, Defaults.http_port_population)
        )

        self.redis_gateway = Redis()
        (
            self.redis_gateway.set_redis_host(redis_host)
            .set_redis_port(redis_port)
            .set_redis_db(redis_db)
        )
        await self.redis_gateway.async_init()

        self.http_server_session_data = SessionDataManagerHttpServer()
        (
            self.http_server_session_data.set_session_data_manager(
                self.redis_gateway
            ).set_http_port(http_port_session_data)
        )
        await self.http_server_session_data.listen()

        self.http_server_population = PopulationCounterHttpServer()
        (
            self.http_server_population.set_population_counter(
                self.redis_gateway
            ).set_http_port(http_port_population)
        )
        await self.http_server_population.listen()

    async def run_forever(self):
        await self.run()

        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(SessionDataManagerMicroservice().run_forever())
