from __future__ import annotations

from requests import Request
from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, Field, Table, KPI
from sbilifeco.cp.metadata_storage.paths import Paths


class MetadataStorageHttpClient(HttpClient, IMetadataStorage):
    def __init__(self):
        HttpClient.__init__(self)

    async def upsert_db(self, db: DB) -> Response[str]:
        try:
            req = Request(
                method="POST", url=f"{self.url_base}{Paths.DB}", json=db.model_dump()
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def delete_db(self, db_id: str) -> Response[None]:
        try:
            req = Request(
                method="DELETE",
                url=f"{self.url_base}{Paths.DB_BY_ID.format(db_id=db_id)}",
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def get_dbs(self) -> Response[list[DB]]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.DB}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                response.payload = [DB.model_validate(db) for db in response.payload]

            return response
        except Exception as e:
            return Response.error(e)

    async def get_db(
        self,
        db_id: str,
        with_tables: bool = False,
        with_fields: bool = False,
        with_kpis: bool = False,
    ) -> Response[DB]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}"
                f"{Paths.DB_BY_ID_WITH_FLAGS.format(db_id=db_id, with_tables=with_tables, with_fields=with_fields, with_kpis=with_kpis)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                db = DB.model_validate(response.payload)
                if db.tables is not None:
                    db.tables = [Table.model_validate(table) for table in db.tables]
                    for table in db.tables:
                        if table.fields is not None:
                            table.fields = [
                                Field.model_validate(field) for field in table.fields
                            ]
                response.payload = db

            return response
        except Exception as e:
            return Response.error(e)

    async def upsert_table(self, db_id, table: Table) -> Response[str]:
        try:
            req = Request(
                method="POST",
                url=f"{self.url_base}{Paths.TABLE.format(db_id=db_id)}",
                json=table.model_dump(),
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def delete_table(self, db_id: str, table_id: str) -> Response[None]:
        try:
            req = Request(
                method="DELETE",
                url=f"{self.url_base}{Paths.TABLE_BY_ID.format(db_id=db_id, table_id=table_id)}",
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def get_tables(self, db_id: str) -> Response[list[Table]]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.TABLE.format(db_id=db_id)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                response.payload = [
                    Table.model_validate(table) for table in response.payload
                ]

            return response
        except Exception as e:
            return Response.error(e)

    async def get_table(
        self, db_id: str, table_id: str, with_fields: bool = False
    ) -> Response[Table]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.TABLE_BY_ID_WITH_FLAGS.format(db_id=db_id, table_id=table_id, with_fields=with_fields)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                table = Table.model_validate(response.payload)
                if table.fields is not None:
                    table.fields = [
                        Field.model_validate(field) for field in table.fields
                    ]
                response.payload = table

            return response
        except Exception as e:
            return Response.error(e)

    async def upsert_kpi(self, db_id: str, kpi: KPI) -> Response[str]:
        try:
            req = Request(
                method="POST",
                url=f"{self.url_base}{Paths.KPI.format(db_id=db_id)}",
                json=kpi.model_dump(),
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def delete_kpi(self, db_id: str, kpi_id: str) -> Response[None]:
        try:
            req = Request(
                method="DELETE",
                url=f"{self.url_base}{Paths.KPI_BY_ID.format(db_id=db_id, kpi_id=kpi_id)}",
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def get_kpis(self, db_id: str) -> Response[list[KPI]]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.KPI.format(db_id=db_id)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                response.payload = [KPI.model_validate(kpi) for kpi in response.payload]

            return response
        except Exception as e:
            return Response.error(e)

    async def get_kpi(self, db_id: str, kpi_id: str) -> Response[KPI]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.KPI_BY_ID.format(db_id=db_id, kpi_id=kpi_id)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                response.payload = KPI.model_validate(response.payload)

            return response
        except Exception as e:
            return Response.error(e)

    async def upsert_field(
        self, db_id: str, table_id: str, field: Field
    ) -> Response[str]:
        try:
            req = Request(
                method="POST",
                url=f"{self.url_base}{Paths.FIELD.format(db_id=db_id, table_id=table_id)}",
                json=field.model_dump(),
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def delete_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[None]:
        try:
            req = Request(
                method="DELETE",
                url=f"{self.url_base}{Paths.FIELD_BY_ID.format(db_id=db_id, table_id=table_id, field_id=field_id)}",
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def get_fields(self, db_id: str, table_id: str) -> Response[list[Field]]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.FIELD.format(db_id=db_id, table_id=table_id)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                response.payload = [
                    Field.model_validate(field) for field in response.payload
                ]

            return response
        except Exception as e:
            return Response.error(e)

    async def get_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[Field]:
        try:
            req = Request(
                method="GET",
                url=f"{self.url_base}{Paths.FIELD_BY_ID.format(db_id=db_id, table_id=table_id, field_id=field_id)}",
            )

            response = await self.request_as_model(req)
            if response.payload is not None:
                response.payload = Field.model_validate(response.payload)

            return response
        except Exception as e:
            return Response.error(e)
