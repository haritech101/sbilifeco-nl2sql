from asyncio import run, sleep
from dotenv import load_dotenv
from sbilifeco.cp.sql_db.mcp.server import SqlDbMCPServer
from sbilifeco.gateways.alchemy import Alchemy
from envvars import EnvVars, Defaults
from os import getenv


class AlchemyMicroservice:
    async def run(self):
        load_dotenv()

        http_port = int(getenv(EnvVars.http_port, Defaults.http_port))
        connection_string = getenv(
            EnvVars.connection_string, Defaults.connection_string
        )
        server_name = getenv(EnvVars.server_name, Defaults.server_name)
        server_instructions = getenv(
            EnvVars.server_instructions, Defaults.server_instructions
        )

        self.sql_db = Alchemy()
        self.sql_db.set_connection_string(connection_string)
        await self.sql_db.async_init()

        self.mcp_server = SqlDbMCPServer()
        (
            self.mcp_server.set_sql_db(self.sql_db)
            .set_server_name(server_name)
            .set_server_instructions(server_instructions)
            .set_http_port(http_port)
        )
        await self.mcp_server.async_init()
        await self.mcp_server.listen()

    async def run_forever(self):
        await self.run()
        while True:
            await sleep(3600)  # Sleep for an hour


if __name__ == "__main__":
    load_dotenv()
    run(AlchemyMicroservice().run_forever())
