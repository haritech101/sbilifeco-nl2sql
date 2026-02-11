from __future__ import annotations
from typing import Optional
from pprint import pprint, pformat
from os import getenv
from asyncio import run, create_task, as_completed
from dotenv import load_dotenv
from pydantic import BaseModel
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from uuid import uuid4
from envvars import Defaults, EnvVars
from yaml import safe_load
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient


class QueryFlowBatchTest:
    def __init__(self):
        self.http_client: QueryFlowHttpClient
        self.query_flow_proto = getenv(
            EnvVars.query_flow_proto, Defaults.query_flow_proto
        )
        self.query_flow_host = getenv(EnvVars.query_flow_host, Defaults.query_flow_host)
        self.query_flow_port = int(
            getenv(EnvVars.query_flow_port, Defaults.query_flow_port)
        )
        self.questions_file = getenv(EnvVars.questions_file, Defaults.questions_file)
        self.db_id = getenv(EnvVars.db_id, Defaults.db_id)
        self.answers_file = getenv(EnvVars.answers_file, Defaults.answers_file)

    async def async_init(self, **kwargs) -> None:
        self.http_client = QueryFlowHttpClient()
        (
            self.http_client.set_proto(self.query_flow_proto)
            .set_host(self.query_flow_host)
            .set_port(self.query_flow_port)
        )

    async def async_shutdown(self, **kwargs) -> None: ...

    async def run(self) -> None:
        with open(self.answers_file, "w") as f:
            f.write("# Answers\n\n")
            f.flush()

        with open(self.questions_file, "r") as f:
            _yaml = safe_load(f)

        questions = _yaml.get("questions", [])

        for i, question in enumerate(questions):
            print(f"Processing question {i+1}/{len(questions)}...")
            response = await self.http_client.query(self.db_id, uuid4().hex, question)
            answer = response.payload if response.is_success else response.message
            correctness = (
                "✅" if (response.payload and "```sql" in response.payload) else "❌"
            )
            print(f"Able to generate SQL: {correctness}")

            with open(self.answers_file, "a") as f:
                f.write(f"### Question\n\n{question}\n\n")
                f.write(f"### Answer {correctness}\n\n{answer}\n\n")
                f.write("---\n\n")
                f.write("---\n\n")
                f.flush()


if __name__ == "__main__":
    load_dotenv()
    test = QueryFlowBatchTest()
    run(test.async_init())
    try:
        run(test.run())
    finally:
        run(test.async_shutdown())
