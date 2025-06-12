from __future__ import annotations
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.query_flow import IQueryFlow
from sbilifeco.models.base import Response


class QueryFlow(IQueryFlow):
    def __init__(self):
        self.metadata_storage: IMetadataStorage
        self.llm: ILLM

    def set_metadata_storage(self, metadata_storage: IMetadataStorage) -> QueryFlow:
        self.metadata_storage = metadata_storage
        return self

    def set_llm(self, llm: ILLM) -> QueryFlow:
        self.llm = llm
        return self

    async def query(self, dbId: str, question: str) -> Response[str]:
        try:
            db_response = await self.metadata_storage.get_db(
                dbId, with_tables=True, with_fields=True, with_kpis=True
            )
            if not db_response.is_success:
                return Response.fail(db_response.message, db_response.code)
            db = db_response.payload
            if db is None:
                return Response.fail("Metadata is inexplicably blank", 500)

            set_metdata_response = await self.llm.set_metadata(db)
            if not set_metdata_response.is_success:
                return Response.fail(
                    set_metdata_response.message, set_metdata_response.code
                )

            query_response = await self.llm.generate_sql(question)
            if not query_response.is_success:
                return Response.fail(query_response.message, query_response.code)
            sql = query_response.payload
            if sql is None:
                return Response.fail("LLM did not return a valid SQL query", 500)

            return Response.ok(sql)
        except Exception as e:
            return Response.error(e)
