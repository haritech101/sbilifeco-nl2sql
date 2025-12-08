from __future__ import annotations
from json import dumps, loads
from re import search
from typing import AsyncIterable, AsyncIterator
from urllib.parse import quote_plus
from uuid import uuid4
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.boundaries.query_flow import IQueryFlow
from sbilifeco.models.base import Response
from datetime import datetime
from pprint import pformat


class QueryFlow(IQueryFlow):
    SUFFIX_METADATA = "-metadata"
    SUFFIX_LAST_QA = "-last-qa"
    SUFFIX_MASTER_VALUES = "-master-values"
    TOOL_CALL_SIGNATURE = r"- Tool name:(.*)\n- Tool input:(.*)"
    MASTER_VALUES_SIGNATURE = (
        r"- Master dimension values evaluated.\n- Dimension:= (.*)\n- Values:= (.*)\n"
    )

    def __init__(self):
        self._metadata_storage: IMetadataStorage
        self._llm: ILLM
        self._session_data_manager: ISessionDataManager
        self._prompt: str

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

    def set_prompt(self, prompt: str) -> QueryFlow:
        self._prompt = prompt
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

    async def query(
        self, dbId: str, session_id: str, question: str, with_thoughts: bool = False
    ) -> Response[str]:
        try:
            print(f"Fetching session data for session: {session_id}", flush=True)
            context_response = await self._session_data_manager.get_session_data(
                f"{session_id}{self.SUFFIX_METADATA}"
            )
            if not context_response.is_success:
                return Response.fail(context_response.message, context_response.code)
            if context_response.payload is None:
                return Response.fail("Metadata is inexplicably None", 500)
            context = context_response.payload

            if context == "":
                print("No pre-saved context found, need to generate", flush=True)

                print(f"Building metadata for dbId: {dbId}", flush=True)
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

                context += self.__fill_in(self._prompt)

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

                cache_response = await self._session_data_manager.get_session_data(
                    f"{dbId}{self.SUFFIX_MASTER_VALUES}"
                )
                if not cache_response.is_success:
                    print(
                        f"Could not get master dimension values due to: {cache_response.message}, continuing",
                        flush=True,
                    )
                elif not cache_response.payload:
                    print("No master dimension values cached, continuing", flush=True)
                else:
                    try:
                        cache = loads(cache_response.payload)
                        pretty_cache = pformat(cache, indent=2)

                        context += (
                            "\n\nHere are some previously cached master dimension values that you can use instead of having to query again: \n\n"
                            f"{pretty_cache}\n\n"
                        )
                    except Exception as e:
                        print(
                            f"Could not parse master dimension values due to: {e}, continuing",
                            flush=True,
                        )

            last_qa_response = await self._session_data_manager.get_session_data(
                f"{session_id}{QueryFlow.SUFFIX_LAST_QA}"
            )
            if not last_qa_response.is_success:
                return Response.fail(last_qa_response.message, last_qa_response.code)
            last_qa = last_qa_response.payload or ""

            session_data = f"{context}\n\n"
            if last_qa:
                session_data += (
                    f"Here is the last question and its answer:\n\n{last_qa}\n\n"
                )

            session_data += (
                f"We are now trying to answer the following question:\n{question}\n\n"
            )
            print(session_data, flush=True)

            loop_num = 0

            print(f"\n\n##### LOOP #{loop_num} #####\n\n", flush=True)
            loop_num += 1

            query_response = await self._llm.generate_reply(session_data)
            if not query_response.is_success:
                return Response.fail(query_response.message, query_response.code)
            if query_response.payload is None:
                return Response.fail("LLM did not return a valid answer", 500)

            answer = query_response.payload
            print(answer, flush=True)

            session_data += answer + "\n\n"
            full_answer = answer + "\n\n"

            master_dim_matches = search(self.MASTER_VALUES_SIGNATURE, answer)
            if not master_dim_matches:
                print("No master dimension values detected, continuing", flush=True)
            elif master_dim_matches is not None:
                dimension = master_dim_matches.group(1).strip()
                values = master_dim_matches.group(2).strip()
                print(
                    f"Detected master dimension values for dimension: {dimension} with values: {values}",
                    flush=True,
                )

                existing = {}
                cache_get_response = await self._session_data_manager.get_session_data(
                    f"{dbId}{self.SUFFIX_MASTER_VALUES}"
                )
                if cache_get_response.is_success:
                    if cache_get_response.payload is not None:
                        try:
                            existing = loads(cache_get_response.payload)
                        except Exception as e:
                            existing = {}
                            print(
                                f"Could not parse existing master dimension values due to: {e}, continuing",
                                flush=True,
                            )

                    existing[dimension] = values
                    cache_set_response = (
                        await self._session_data_manager.update_session_data(
                            f"{dbId}{self.SUFFIX_MASTER_VALUES}",
                            dumps(existing),
                        )
                    )
                    if not cache_set_response.is_success:
                        print(
                            f"Could not save updated master dimension values due to: {cache_set_response.message}, continuing",
                            flush=True,
                        )

            await self._session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_METADATA}", context
            )

            await self._session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_LAST_QA}", f"{question}\n\n{answer}\n\n"
            )

            return Response.ok(with_thoughts and full_answer.strip() or answer.strip())
        except Exception as e:
            return Response.error(e)
