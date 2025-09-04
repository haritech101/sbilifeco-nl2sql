from __future__ import annotations
from typing import AsyncIterable, AsyncIterator
from uuid import uuid4
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.boundaries.query_flow import IQueryFlow
from sbilifeco.models.base import Response
from datetime import datetime


class QueryFlow(IQueryFlow):
    SUFFIX_METADATA = "-metadata"
    SUFFIX_LAST_QA = "-last-qa"

    def __init__(self):
        self._metadata_storage: IMetadataStorage
        self._llm: ILLM
        self._session_data_manager: ISessionDataManager
        self._prompts: AsyncIterator[str]

    def set_metadata_storage(self, metadata_storage: IMetadataStorage) -> QueryFlow:
        self._metadata_storage = metadata_storage
        return self

    def set_llm(self, llm: ILLM) -> QueryFlow:
        self._llm = llm
        return self

    def set_session_data_manager(
        self, session_data_manager: ISessionDataManager
    ) -> QueryFlow:
        self._session_data_manager = session_data_manager
        return self

    def set_prompts(self, prompts: AsyncIterator[str]) -> QueryFlow:
        self._prompts = prompts
        return self

    async def start_session(self) -> Response[str]:
        return Response.ok(uuid4().hex)

    async def stop_session(self, session_id: str) -> Response[None]:
        try:
            await self._session_data_manager.delete_session_data(
                f"{session_id}{self.SUFFIX_LAST_QA}"
            )
            await self._session_data_manager.delete_session_data(
                f"{session_id}{self.SUFFIX_METADATA}"
            )

            # All good
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def reset_session(self, session_id: str) -> Response[None]:
        try:
            await self._session_data_manager.delete_session_data(
                f"{session_id}{self.SUFFIX_LAST_QA}"
            )
            await self._session_data_manager.delete_session_data(
                f"{session_id}{self.SUFFIX_METADATA}"
            )

            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    def __fill_in(self, template: str) -> str:
        now = datetime.now()
        filled_in = template.format(this_month=now.strftime("%b %Y"))
        return filled_in

    async def query(self, dbId: str, session_id: str, question: str) -> Response[str]:
        try:
            context_response = await self._session_data_manager.get_session_data(
                f"{session_id}{self.SUFFIX_METADATA}"
            )
            if not context_response.is_success:
                return Response.fail(context_response.message, context_response.code)
            if context_response.payload is None:
                return Response.fail("Metadata is inexplicably None", 500)
            context = context_response.payload

            if context == "":
                db_response = await self._metadata_storage.get_db(
                    dbId,
                    with_tables=True,
                    with_fields=True,
                    with_kpis=True,
                    with_additional_info=True,
                )
                if not db_response.is_success:
                    return Response.fail(db_response.message, db_response.code)
                db = db_response.payload
                if db is None:
                    return Response.fail("Metadata is inexplicably blank", 500)

                preamble = await anext(self._prompts, "")
                if preamble:
                    context += self.__fill_in(preamble) + "\n\n"

                context += (
                    "Here are the details of the database you will be querying.\n\n"
                )
                context += f"Database name: {db.name}\n"
                if db.description:
                    context += f"Database description: {db.description}\n"
                if db.tables is not None:
                    for table in db.tables:
                        context += f"\tTable name: {table.name}\n"
                        context += f"\tTable description: {table.description}\n"
                        if table.fields is not None:
                            for field in table.fields:
                                context += f"\t\tField name: {field.name}, type: {field.type}\n"
                                if field.description:
                                    context += (
                                        f"\t\tField description: {field.description}\n"
                                    )
                                if field.aka:
                                    context += f"\t\tOther names for field '{field.name}': {field.aka}\n"

                if db.kpis:
                    context += "KPIs:\n"
                    for kpi in db.kpis:
                        context += f"\tKPI name: {kpi.name}\n"
                        context += f"\tKPI other names: {kpi.aka}\n"
                        context += f"\tKPI description: {kpi.description}\n"
                        context += f"\tKPI formula: {kpi.formula}\n"

                if db.additional_info:
                    context += (
                        "Also keep in mind the following additional points.\n"
                        f"{db.additional_info}\n"
                    )
            else:
                _ = await anext(self._prompts, "")

            last_qa_response = await self._session_data_manager.get_session_data(
                f"{session_id}{QueryFlow.SUFFIX_LAST_QA}"
            )
            if not last_qa_response.is_success:
                return Response.fail(last_qa_response.message, last_qa_response.code)
            last_qa = last_qa_response.payload or ""

            if last_qa:
                context += f"Here is the last question and its answer:\n\n{last_qa}\n\n"

            session_data = f"{context}\n\n"

            session_data += (
                f"We are now trying to answer the following question:\n{question}\n\n"
            )
            session_data += (
                "If you have understood so far, please reply with 'Understood'.\n\n"
            )

            query_response = await self._llm.generate_reply(session_data)
            if not query_response.is_success:
                return Response.fail(query_response.message, query_response.code)
            if query_response.payload is None:
                return Response.fail("LLM did not return a valid SQL query", 500)

            answer = query_response.payload
            full_answer = ""
            async for prompt in self._prompts:
                session_data += f"{prompt}\n\n"
                full_answer += f"{prompt}\n\n"
                query_response = await self._llm.generate_reply(session_data)

                if not query_response.is_success:
                    return Response.fail(query_response.message, query_response.code)
                answer = query_response.payload
                if answer is None:
                    return Response.fail("LLM did not return a valid SQL query", 500)

                session_data += answer + "\n\n"
                full_answer += answer + "\n\n"

            await self._session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_METADATA}", context
            )

            await self._session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_LAST_QA}", f"{question}\n\n{answer}\n\n"
            )

            return Response.ok(full_answer.strip())
        except Exception as e:
            return Response.error(e)
