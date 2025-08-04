from __future__ import annotations
from json import dumps
from sbilifeco.boundaries.llm import ILLM, ChatMessage
from google.genai import Client
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB
from datetime import datetime


class Gemini(ILLM):
    def __init__(self):
        self.model: str = "gemini-1.5-flash"
        self.api_key: str
        self.client: Client
        self.context: list[str] = []
        self.preamble = ""
        self.postamble = ""

    def set_model(self, model: str) -> Gemini:
        self.model = model
        return self

    def set_api_key(self, api_key: str) -> Gemini:
        self.api_key = api_key
        return self

    async def set_preamble(self, instruction: str) -> Response[None]:
        self.preamble = instruction
        return Response.ok(None)

    async def set_postamble(self, instruction: str) -> Response[None]:
        self.postamble = instruction
        return Response.ok(None)

    def __fill_in(self, template: str) -> str:
        return template.format(this_month=datetime.now().strftime("%b %Y"))

    async def async_init(self) -> None:
        self.client = Client(api_key=self.api_key)
        self.context: list[str] = [self.__fill_in(self.preamble)]

    async def add_context(self, context: list[ChatMessage]) -> Response[None]:
        try:
            self.context.extend([message.content for message in context])
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def reset_context(self) -> Response[None]:
        try:
            self.client = None
            self.context = []
            await self.async_init()
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def set_metadata(self, db: DB) -> Response[None]:
        try:
            self.context.append(
                "The query will be based on the following database metadata:\n"
            )
            self.context.append(f"Database name: {db.name}\n")
            self.context.append(f"Database description: {db.description}\n")
            if db.tables is not None:
                for table in db.tables:
                    self.context.append(f"\tTable name: {table.name}\n")
                    self.context.append(f"\tTable description: {table.description}\n")
                    if table.fields is not None:
                        for field in table.fields:
                            self.context.append(
                                f"\t\tField name: {field.name}, type: {field.type}\n"
                            )
                            self.context.append(
                                f"\t\tField description: {field.description}\n"
                            )
                            self.context.append(
                                f"\t\tOther names for field '{field.name}': {field.aka}\n"
                            )
            if db.kpis is not None:
                self.context.append("KPIs:\n")
                for kpi in db.kpis:
                    self.context.append(f"\tKPI name: {kpi.name}\n")
                    self.context.append(f"\tKPI other names: {kpi.aka}\n")
                    self.context.append(f"\tKPI description: {kpi.description}\n")
                    self.context.append(f"\tKPI formula: {kpi.formula}\n")
            else:
                self.context.append("No KPIs are defined for this database.\n")

            if db.additional_info is not None:
                self.context.append(
                    "Also keep in mind the following additional points.\n"
                    f"{db.additional_info or "No additional points provided"}\n"
                )

            if self.postamble:
                self.context.append(self.__fill_in(self.postamble))

            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def generate_sql(self, question: str) -> Response[str]:
        try:
            line = f"\nGenerate a query against this question/statement:\n{question}\n"
            self.context.append(line)
            challenge = "".join([item for item in self.context])

            print(challenge)
            print(f"{len(challenge)} characters consumed\n")

            gemini_response = self.client.models.generate_content(
                model=self.model, contents=challenge
            )
            answer = (gemini_response.text or "").strip()
            self.context.append(answer)

            return Response.ok(answer)
        except Exception as e:
            return Response.error(e)
