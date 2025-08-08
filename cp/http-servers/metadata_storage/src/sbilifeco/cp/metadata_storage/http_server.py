from __future__ import annotations
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.cp.metadata_storage.paths import Paths
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, Table, Field, KPI


class MetadataStorageMicroservice(HttpServer):
    def __init__(self):
        HttpServer.__init__(self)
        self.storage: IMetadataStorage

    def set_metadata_storage(
        self, storage: IMetadataStorage
    ) -> MetadataStorageMicroservice:
        self.storage = storage
        return self

    async def start(self) -> None:
        await HttpServer.listen(self)

    async def stop(self) -> None:
        await HttpServer.stop(self)

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(Paths.DB)
        async def upsert_db(db: DB) -> Response[str]:
            try:
                return await self.storage.upsert_db(db)
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.DB_BY_ID)
        async def delete_db(db_id: str) -> Response[None]:
            try:
                return await self.storage.delete_db(db_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.DB)
        async def get_dbs() -> Response[list[DB]]:
            try:
                return await self.storage.get_dbs()
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.DB_BY_ID)
        async def get_db(
            db_id: str,
            with_tables: bool = False,
            with_fields: bool = False,
            with_kpis: bool = False,
            with_additional_info: bool = False,
        ) -> Response[DB]:
            try:
                return await self.storage.get_db(
                    db_id, with_tables, with_fields, with_kpis, with_additional_info
                )
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.TABLE)
        async def upsert_table(db_id: str, table: Table) -> Response[str]:
            try:
                return await self.storage.upsert_table(db_id, table)
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.TABLE_BY_ID)
        async def delete_table(db_id: str, table_id: str) -> Response[None]:
            try:
                return await self.storage.delete_table(db_id, table_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.TABLE)
        async def get_tables(db_id: str) -> Response[list[Table]]:
            try:
                return await self.storage.get_tables(db_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.TABLE_BY_ID)
        async def get_table(
            db_id: str, table_id: str, with_fields: bool = False
        ) -> Response[Table]:
            try:
                return await self.storage.get_table(db_id, table_id, with_fields)
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.KPI)
        async def upsert_kpi(db_id: str, kpi: KPI) -> Response[str]:
            try:
                return await self.storage.upsert_kpi(db_id, kpi)
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.KPI_BY_ID)
        async def delete_kpi(db_id: str, kpi_id: str) -> Response[None]:
            try:
                return await self.storage.delete_kpi(db_id, kpi_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.KPI)
        async def get_kpis(db_id: str) -> Response[list[KPI]]:
            try:
                return await self.storage.get_kpis(db_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.KPI_BY_ID)
        async def get_kpi(db_id: str, kpi_id: str) -> Response[KPI]:
            try:
                return await self.storage.get_kpi(db_id, kpi_id)
            except Exception as e:
                return Response.error(e)

        @self.post(Paths.FIELD)
        async def upsert_field(
            db_id: str, table_id: str, field: Field
        ) -> Response[str]:
            try:
                return await self.storage.upsert_field(db_id, table_id, field)
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.FIELD_BY_ID)
        async def delete_field(
            db_id: str, table_id: str, field_id: str
        ) -> Response[None]:
            try:
                return await self.storage.delete_field(db_id, table_id, field_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.FIELD)
        async def get_fields(db_id: str, table_id: str) -> Response[list[Field]]:
            try:
                return await self.storage.get_fields(db_id, table_id)
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.FIELD_BY_ID)
        async def get_field(
            db_id: str, table_id: str, field_id: str
        ) -> Response[Field]:
            try:
                return await self.storage.get_field(db_id, table_id, field_id)
            except Exception as e:
                return Response.error(e)
