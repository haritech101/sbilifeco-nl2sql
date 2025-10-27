from __future__ import annotations
from curses import meta
from random import randint
from sbilifeco.cp.llm.http_client import LLMHttpClient
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.models.base import Response
from pprint import pprint
from dotenv import load_dotenv
from os import getenv
from envvars import EnvVars, Defaults
from asyncio import run


class QGen:
    def __init__(self):
        self.llm: LLMHttpClient
        self.metadata_storage: MetadataStorageHttpClient
        self.llm_proto: str
        self.llm_host: str
        self.llm_port: int
        self.llm_template_file: str
        self.metadata_storage_proto: str
        self.metadata_storage_host: str
        self.metadata_storage_port: int
        self.db_id: str

    def set_llm_details(
        self, proto: str, host: str, port: int, template_file: str
    ) -> QGen:
        self.llm_proto = proto
        self.llm_host = host
        self.llm_port = port
        self.llm_template_file = template_file
        return self

    def set_metadata_storage_details(
        self, proto: str, host: str, port: int, db_id: str
    ) -> QGen:
        self.metadata_storage_proto = proto
        self.metadata_storage_host = host
        self.metadata_storage_port = port
        self.db_id = db_id
        return self

    async def async_init(self):
        self.llm = LLMHttpClient()
        self.llm.set_proto(self.llm_proto).set_host(self.llm_host).set_port(
            self.llm_port
        )

        self.metadata_storage = MetadataStorageHttpClient()
        self.metadata_storage.set_proto(self.metadata_storage_proto).set_host(
            self.metadata_storage_host
        ).set_port(self.metadata_storage_port)

    async def async_shutdown(self): ...

    async def generate(
        self,
        num_questions: int = 10,
        num_variations=3,
        extra_question: str | None = None,
    ) -> Response[str]:
        try:
            prompt_response = await self._generate_prompt(
                num_questions, num_variations, extra_question
            )
            if not prompt_response.is_success:
                return Response.fail(prompt_response.message, prompt_response.code)
            elif not prompt_response.payload:
                return Response.fail("Prompt is inexplicably empty", 500)
            prompt = prompt_response.payload

            pprint(prompt)

            llm_response = await self.llm.generate_reply(prompt)
            if not llm_response.is_success:
                return Response.fail(llm_response.message, llm_response.code)
            elif not llm_response.payload:
                return Response.fail("LLM reply is inexplicably empty", 500)
            reply = llm_response.payload

            with open(".local/reply.md", "w") as md:
                md.write(reply)

            return Response.ok(reply)
        except Exception as e:
            return Response.error(e)

    async def _generate_prompt(
        self,
        num_questions: int = 10,
        num_variations=3,
        extra_question: str | None = None,
    ) -> Response[str]:
        template = ""
        with open(self.llm_template_file, "r") as f:
            template = f.read()

        metadata_response = await self.metadata_storage.get_db(
            self.db_id, with_tables=True, with_fields=True
        )
        if not metadata_response.is_success:
            return Response.fail(metadata_response.message, metadata_response.code)
        elif not metadata_response.payload:
            return Response.fail("Payload is inexplicably empty", 500)

        metadata = metadata_response.payload
        metadata_as_prompt = (
            f"Database Name: {metadata.name}\n"
            f"Database Description: {metadata.description}\n\n"
        )
        if metadata.tables:
            for table in metadata.tables:
                metadata_as_prompt += (
                    f"  - Table: {table.name}\n"
                    f"    Table Description: {table.description}\n"
                )
                if table.fields:
                    for field in table.fields:
                        metadata_as_prompt += (
                            f"      - Field: {field.name}\n"
                            f"        Field Description: {field.description}\n"
                            f"        Field Type: {field.type}\n"
                        )

        prompt = template.replace("{{metadata}}", metadata_as_prompt)
        prompt = prompt.replace("{{n}}", f"{num_questions}")
        prompt = prompt.replace("{{v}}", f"{num_variations}")
        prompt = prompt.replace("{{rn}}", f"{randint(1, 100000)}")

        prompt = prompt.replace(
            "{{question}}", f"Then answer the question: {extra_question}" or ""
        )

        return Response.ok(prompt)


async def run_qgen() -> None:
    db_id = getenv(EnvVars.db_id, "")
    llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
    llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
    llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))
    llm_template_file = getenv(EnvVars.llm_template_file, Defaults.llm_template_file)
    metadata_storage_proto = getenv(
        EnvVars.metadata_storage_proto, Defaults.metadata_storage_proto
    )
    metadata_storage_host = getenv(
        EnvVars.metadata_storage_host, Defaults.metadata_storage_host
    )
    metadata_storage_port = int(
        getenv(EnvVars.metadata_storage_port, Defaults.metadata_storage_port)
    )
    num_questions = int(getenv(EnvVars.num_questions, Defaults.num_questions))
    num_variations = int(getenv(EnvVars.num_variations, Defaults.num_variations))

    qgen = (
        QGen()
        .set_llm_details(llm_proto, llm_host, llm_port, llm_template_file)
        .set_metadata_storage_details(
            metadata_storage_proto,
            metadata_storage_host,
            metadata_storage_port,
            db_id,
        )
    )

    await qgen.async_init()
    try:
        response = await qgen.generate(
            num_questions=num_questions, num_variations=num_variations
        )
        if response.is_success:
            pprint(response.payload)
        else:
            print(f"Error: {response.message} (code: {response.code})")
    finally:
        await qgen.async_shutdown()


if __name__ == "__main__":
    load_dotenv()
    run(run_qgen())
