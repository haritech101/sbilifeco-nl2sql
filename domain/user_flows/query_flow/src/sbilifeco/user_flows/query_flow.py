from __future__ import annotations
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
        self.metadata_storage: IMetadataStorage
        self.llm: ILLM
        self.session_data_manager: ISessionDataManager
        self.preamble = ""
        self.postamble = ""

    def set_metadata_storage(self, metadata_storage: IMetadataStorage) -> QueryFlow:
        self.metadata_storage = metadata_storage
        return self

    def set_llm(self, llm: ILLM) -> QueryFlow:
        self.llm = llm
        return self

    def set_session_data_manager(
        self, session_data_manager: ISessionDataManager
    ) -> QueryFlow:
        self.session_data_manager = session_data_manager
        return self

    def set_preamble(self, preamble: str) -> QueryFlow:
        self.preamble = preamble
        return self

    def set_postamble(self, postamble: str) -> QueryFlow:
        self.postamble = postamble
        return self

    async def start_session(self) -> Response[str]:
        return Response.ok(uuid4().hex)

    async def stop_session(self, session_id: str) -> Response[None]:
        try:
            delete_response = await self.session_data_manager.delete_session_data(
                session_id
            )
            if not delete_response.is_success:
                return Response.fail(delete_response.message, delete_response.code)

            # All good
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def reset_session(self, session_id: str) -> Response[None]:
        try:
            delete_response = await self.session_data_manager.delete_session_data(
                session_id
            )
            if not delete_response.is_success:
                return Response.fail(delete_response.message, delete_response.code)

            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    def __fill_in(self, template: str) -> str:
        now = datetime.now()
        filled_in = template.format(this_month=now.strftime("%b %Y"))
        return filled_in

    async def query(self, dbId: str, session_id: str, question: str) -> Response[str]:
        try:
            metadata_response = await self.session_data_manager.get_session_data(
                f"{session_id}{self.SUFFIX_METADATA}"
            )
            if not metadata_response.is_success:
                return Response.fail(metadata_response.message, metadata_response.code)
            if metadata_response.payload is None:
                return Response.fail("Metadata is inexplicably None", 500)
            metadata = metadata_response.payload

            if metadata == "":
                db_response = await self.metadata_storage.get_db(
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

                if self.preamble:
                    metadata += self.__fill_in(self.preamble) + "\n\n"

                metadata += (
                    "The query will be based on the following database metadata:\n"
                )

                metadata += f"Database name: {db.name}\n"
                if db.description:
                    metadata += f"Database description: {db.description}\n"
                if db.tables is not None:
                    for table in db.tables:
                        metadata += f"\tTable name: {table.name}\n"
                        metadata += f"\tTable description: {table.description}\n"
                        if table.fields is not None:
                            for field in table.fields:
                                metadata += f"\t\tField name: {field.name}, type: {field.type}\n"
                                if field.description:
                                    metadata += (
                                        f"\t\tField description: {field.description}\n"
                                    )
                                if field.aka:
                                    metadata += f"\t\tOther names for field '{field.name}': {field.aka}\n"

                if db.kpis:
                    metadata += "KPIs:\n"
                    for kpi in db.kpis:
                        metadata += f"\tKPI name: {kpi.name}\n"
                        metadata += f"\tKPI other names: {kpi.aka}\n"
                        metadata += f"\tKPI description: {kpi.description}\n"
                        metadata += f"\tKPI formula: {kpi.formula}\n"

                if db.additional_info:
                    metadata += (
                        "Also keep in mind the following additional points.\n"
                        f"{db.additional_info}\n"
                    )

                if self.postamble:
                    metadata += self.__fill_in(self.postamble) + "\n\n"

            last_qa_response = await self.session_data_manager.get_session_data(
                f"{session_id}{QueryFlow.SUFFIX_LAST_QA}"
            )
            if not last_qa_response.is_success:
                return Response.fail(last_qa_response.message, last_qa_response.code)
            last_qa = last_qa_response.payload or ""

            session_data = f"{metadata}\n\n"
            session_data += (
                f"{last_qa}\n\nKeeping the last query as it is,\n" if last_qa else ""
            )

            session_data += f"\n{question}\n"

            query_response = await self.llm.generate_reply(session_data)
            if not query_response.is_success:
                return Response.fail(query_response.message, query_response.code)
            answer = query_response.payload
            if answer is None:
                return Response.fail("LLM did not return a valid SQL query", 500)

            await self.session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_METADATA}", metadata
            )

            await self.session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_LAST_QA}", f"{question}\n\n{answer}\n\n"
            )

            return Response.ok(answer)
        except Exception as e:
            return Response.error(e)
