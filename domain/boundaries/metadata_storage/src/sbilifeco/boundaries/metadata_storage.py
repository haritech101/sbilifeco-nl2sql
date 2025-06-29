from __future__ import annotations
from typing import Protocol

from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, Table, Field, KPI


class IMetadataStorage(Protocol):
    async def upsert_db(self, db: DB) -> Response[str]:
        raise NotImplementedError()

    async def delete_db(self, db_id: str) -> Response[None]:
        raise NotImplementedError()

    async def get_dbs(self) -> Response[list[DB]]:
        raise NotImplementedError()

    async def get_db(
        self,
        db_id: str,
        with_tables: bool = False,
        with_fields: bool = False,
        with_kpis: bool = False,
        with_additional_info: bool = False,
    ) -> Response[DB]:
        raise NotImplementedError()

    async def upsert_table(self, db_id, table: Table) -> Response[str]:
        raise NotImplementedError()

    async def delete_table(self, db_id: str, table_id: str) -> Response[None]:
        raise NotImplementedError()

    async def get_tables(self, db_id: str) -> Response[list[Table]]:
        raise NotImplementedError()

    async def get_table(
        self, db_id: str, table_id: str, with_fields: bool = False
    ) -> Response[Table]:
        raise NotImplementedError()

    async def upsert_field(
        self, db_id: str, table_id: str, field: Field
    ) -> Response[str]:
        raise NotImplementedError()

    async def delete_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[None]:
        raise NotImplementedError()

    async def get_fields(self, db_id: str, table_id: str) -> Response[list[Field]]:
        raise NotImplementedError()

    async def get_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[Field]:
        raise NotImplementedError()

    async def upsert_kpi(self, db_id: str, kpi: KPI) -> Response[str]:
        raise NotImplementedError()

    async def delete_kpi(self, db_id: str, kpi_id: str) -> Response[None]:
        raise NotImplementedError()

    async def get_kpis(self, db_id: str) -> Response[list[KPI]]:
        raise NotImplementedError()

    async def get_kpi(self, db_id: str, kpi_id: str) -> Response[KPI]:
        raise NotImplementedError()
