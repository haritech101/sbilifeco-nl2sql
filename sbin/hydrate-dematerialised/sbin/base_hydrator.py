from __future__ import annotations
from asyncio import run as run
from dotenv import load_dotenv as load_dotenv
from sqlalchemy import create_engine, Engine, Connection, select as select, func as func
from sqlalchemy.orm import Session as Session
from random import seed as seed, choice as choice, randint as randint
from uuid import uuid4 as uuid4
from faker import Faker
from datetime import date as date
from os import getenv as getenv
from sbin.envvars import EnvVars as EnvVars, Defaults as Defaults
from sbin import model as model


class BaseHydrator:
    def __init__(self) -> None:
        self.conn_string = ""
        self.engine: Engine
        self.conn: Connection
        self.faker = Faker()

    def set_conn_string(self, conn_string: str) -> BaseHydrator:
        self.conn_string = conn_string
        return self

    async def async_init(self) -> None:
        self.engine = create_engine(self.conn_string)

    async def async_shutdown(self) -> None:
        self.engine.dispose()

    async def run_as_tool(self) -> None:
        load_dotenv()

        conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)
        self.set_conn_string(conn_string)

        await self.async_init()
        await self.hydrate()
        await self.async_shutdown()

    async def hydrate(self) -> None: ...
