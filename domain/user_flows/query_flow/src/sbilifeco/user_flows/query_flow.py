from __future__ import annotations
from json import dumps, loads
from re import search
from typing import Sequence
from urllib.parse import quote_plus
from uuid import uuid4
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.boundaries.tool_support import (
    IExternalToolRepo,
    ExternalTool,
    ExternalToolParams,
)
from sbilifeco.boundaries.query_flow import IQueryFlow
from sbilifeco.models.base import Response
from datetime import datetime
from pprint import pformat


class QueryFlow(IQueryFlow):
    SUFFIX_METADATA = "-metadata"
    SUFFIX_LAST_QA = "-last-qa"
    SUFFIX_MASTER_VALUES = "-master-values"
    PLACEHOLDER_METADATA = "db_metadata"
    PLACEHOLDER_LAST_QA = "last_qa"
    PLACEHOLDER_QUESTION = "question"
    PLACEHOLDER_MASTER_VALUES = "master_values"
    PLACEHOLDER_THIS_MONTH = "this_month"
    PLACEHOLDER_TOOLS = "tools_available"
    TOOL_CALL_SIGNATURE = r"- Tool name:(.*)\n(.*)- Tool input:.*(\{.*\}).*"

    def __init__(self):
        self._metadata_storage: IMetadataStorage
        self._llm: ILLM
        self._session_data_manager: ISessionDataManager
        self._prompt: str
        self._external_tool_repo: IExternalToolRepo
        self._external_tools: list[ExternalTool] = []
        self._is_tool_call_enabled: bool = False

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

    def set_external_tool_repo(
        self, external_tool_repo: IExternalToolRepo
    ) -> QueryFlow:
        self._external_tool_repo = external_tool_repo
        return self

    def set_is_tool_call_enabled(self, is_enabled: bool) -> QueryFlow:
        self._is_tool_call_enabled = is_enabled
        return self

    async def async_init(self) -> None:
        if self._is_tool_call_enabled and self._external_tool_repo is not None:
            tools = await self._external_tool_repo.fetch_tools()
            self._external_tools.extend(tools)

    async def async_shutdown(self) -> None:
        self._external_tools.clear()

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

    async def query(
        self, dbId: str, session_id: str, question: str, with_thoughts: bool = False
    ) -> Response[str]:
        try:
            print(f"Fetching cached db metadata for session: {session_id}", flush=True)
            cached_db_metadata_response = (
                await self._session_data_manager.get_session_data(
                    f"{session_id}{self.SUFFIX_METADATA}"
                )
            )
            if not cached_db_metadata_response.is_success:
                return Response.fail(
                    cached_db_metadata_response.message,
                    cached_db_metadata_response.code,
                )
            if cached_db_metadata_response.payload is None:
                return Response.fail("Metadata is inexplicably None", 500)
            db_metadata = cached_db_metadata_response.payload

            # DB metadata, try cache, otherwise build
            if db_metadata == "":
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

                db_metadata = ""
                db_metadata += f"Database name: {db.name}\n"
                if db.description:
                    db_metadata += f"Database description: {db.description}\n"
                if db.tables is not None:
                    for table in db.tables:
                        db_metadata += f"\tTable name: {table.name}\n"
                        db_metadata += f"\tTable description: {table.description}\n"
                        if table.fields is not None:
                            for field in table.fields:
                                db_metadata += f"\t\tField name: {field.name}, type: {field.type}\n"
                                if field.description:
                                    db_metadata += (
                                        f"\t\tField description: {field.description}\n"
                                    )
                                if field.aka:
                                    db_metadata += f"\t\tOther names for field '{field.name}': {field.aka}\n"
                if db.kpis:
                    db_metadata += "KPIs:\n"
                    for kpi in db.kpis:
                        db_metadata += f"\tKPI name: {kpi.name}\n"
                        db_metadata += f"\tKPI other names: {kpi.aka}\n"
                        db_metadata += f"\tKPI description: {kpi.description}\n"
                        db_metadata += f"\tKPI formula: {kpi.formula}\n"

                if db.additional_info:
                    db_metadata += (
                        "Also keep in mind the following additional points.\n"
                        f"{db.additional_info}\n"
                    )
            else:
                print("Pre-saved db metadata found, using it", flush=True)

            # Master values, try cache
            master_values = "Not defined"
            cached_master_values = await self._session_data_manager.get_session_data(
                f"{dbId}{self.SUFFIX_MASTER_VALUES}"
            )
            if not cached_master_values.is_success:
                print(
                    f"Could not get master dimension values due to: {cached_master_values.message}, continuing",
                    flush=True,
                )
            elif not cached_master_values.payload:
                print("No master dimension values cached, continuing", flush=True)
            else:
                try:
                    cache = loads(cached_master_values.payload)
                    master_values = pformat(cache, indent=2)
                except Exception as e:
                    print(
                        f"Could not parse master dimension values due to: {e}, continuing",
                        flush=True,
                    )

            # Last question and answer
            cached_last_qa_response = await self._session_data_manager.get_session_data(
                f"{session_id}{QueryFlow.SUFFIX_LAST_QA}"
            )
            if not cached_last_qa_response.is_success:
                return Response.fail(
                    cached_last_qa_response.message, cached_last_qa_response.code
                )
            last_qa = cached_last_qa_response.payload or "None"

            if not self._external_tools:
                tools_available = "No external tools are available."
            else:
                tools_available = "The following external tools are available:\n"
                for tool in self._external_tools:
                    tools_available += f"- Tool name: {tool.name}\n"
                    tools_available += f"  Description: {tool.description}\n"
                    tools_available += f"  Parameters:\n"
                    for param in tool.params:
                        tools_available += (
                            f"    - Name: {param.name}\n"
                            f"      Description: {param.description}\n"
                            f"      Type: {param.type}\n"
                        )

            template_map = {
                self.PLACEHOLDER_METADATA: db_metadata,
                self.PLACEHOLDER_LAST_QA: last_qa,
                self.PLACEHOLDER_QUESTION: question,
                self.PLACEHOLDER_MASTER_VALUES: master_values,
                self.PLACEHOLDER_THIS_MONTH: datetime.now().strftime("%B %Y"),
                self.PLACEHOLDER_TOOLS: tools_available,
            }

            next_full_prompt = self._prompt.format_map(template_map)
            print(next_full_prompt, flush=True)

            query_response = await self._llm.generate_reply(next_full_prompt)
            if not query_response.is_success:
                return Response.fail(query_response.message, query_response.code)
            if query_response.payload is None:
                return Response.fail("LLM did not return a valid answer", 500)

            answer = query_response.payload
            print(answer, flush=True)

            full_answer = next_full_prompt + "\n\n" + answer + "\n\n"

            tool_call_match = search(self.TOOL_CALL_SIGNATURE, answer)
            while (
                self._is_tool_call_enabled and self._external_tools and tool_call_match
            ):
                tool_name, _, tool_params = tool_call_match.groups()
                tool_name = tool_name.strip()

                tool_params = tool_params.strip()
                tool_params = loads(tool_params)

                print(
                    f"Invoking tool: {tool_name} with params: {tool_params}\n\n",
                    flush=True,
                )
                tool_response = await self._external_tool_repo.invoke_tool(
                    tool_name, **tool_params
                )

                print(f"Tool response: {dumps(tool_response)}\n\n", flush=True)

                next_full_prompt += (
                    f"Tool answer: {dumps(tool_response)}\n\nProceed\n\n"
                )

                query_response = await self._llm.generate_reply(next_full_prompt)
                if not query_response.is_success:
                    return Response.fail(query_response.message, query_response.code)
                if query_response.payload is None:
                    return Response.fail("LLM did not return a valid answer", 500)
                answer = query_response.payload
                print(answer, flush=True)

                full_answer += answer + "\n\n"

                tool_call_match = search(self.TOOL_CALL_SIGNATURE, answer)

            # Save updated metadata and last QA
            if not cached_db_metadata_response.payload:
                await self._session_data_manager.update_session_data(
                    f"{session_id}{self.SUFFIX_METADATA}", db_metadata
                )

            await self._session_data_manager.update_session_data(
                f"{session_id}{self.SUFFIX_LAST_QA}", f"{question}\n\n{answer}\n\n"
            )

            return Response.ok(with_thoughts and full_answer.strip() or answer.strip())
        except Exception as e:
            return Response.error(e)
