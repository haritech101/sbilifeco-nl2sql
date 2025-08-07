from asyncio import run, sleep
from os import getenv
from dotenv import load_dotenv
from sbilifeco.gateways.redis import Redis
from sbilifeco.cp.session_data_manager.microservice import (
    SessionDataManagerMicroservice,
)
from envvars import EnvVars, Defaults


class ServiceDataManagerExecutable:
    async def run(self):
        redis_host = getenv(EnvVars.redis_host, Defaults.redis_host)
        redis_port = int(getenv(EnvVars.redis_port, Defaults.redis_port))
        redis_db = int(getenv(EnvVars.redis_db, Defaults.redis_db))
        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))

        self.session_data_manager = Redis()
        (
            self.session_data_manager.set_redis_host(redis_host)
            .set_redis_port(redis_port)
            .set_redis_db(redis_db)
        )
        await self.session_data_manager.async_init()

        self.http_server = SessionDataManagerMicroservice()
        (
            self.http_server.set_session_data_manager(
                self.session_data_manager
            ).set_http_port(http_port)
        )
        await self.http_server.listen()

    async def run_forever(self):
        await self.run()

        while True:
            await sleep(3600)


if __name__ == "__main__":
    load_dotenv()
    run(ServiceDataManagerExecutable().run_forever())
