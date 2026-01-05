from __future__ import annotations
from typing import cast
from sbilifeco.models.base import Response
from sys import path, modules
from pprint import pprint

# Import other required contracts/modules here
from pathlib import Path
from importlib import import_module
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.models.db_metadata import DB, Field, Table
from sqlalchemy import Table as AlchemyTable


class SQLAlchemyGateway(IMetadataStorage):
    def __init__(self):
        self.definitions_path = ""

    def set_definitions_path(self, path: str) -> None:
        self.definitions_path = path

    async def async_init(self) -> None:
        path.append(self.definitions_path)

    async def async_shutdown(self) -> None: ...

    def _get_db_info(self, py_file: Path) -> DB | None:
        try:
            with open(py_file, "r") as f:
                name = ""
                description = ""
                for line in f:
                    if line.startswith('"""Name:'):
                        name = line.split(":", 1)[1].strip().strip('"""')
                    elif line.startswith('"""Description:'):
                        description = line.split(":", 1)[1].strip().strip('"""')
                return DB(
                    id=py_file.stem,
                    name=name,
                    description=description,
                )
        except Exception:
            return None

    async def get_dbs(self) -> Response[list[DB]]:
        try:
            py_files = Path(self.definitions_path).glob("*.py")
            dbs = [self._get_db_info(py_file) for py_file in py_files]
            dbs = [db for db in dbs if db is not None]
            return Response.ok(dbs)
        except Exception as e:
            return Response.error(e)

    async def get_tables(self, db_id: str) -> Response[list[Table]]:
        try:
            the_db = import_module(db_id)

            tables = [
                Table(
                    id=key,
                    name=sqltable.fullname,
                    description=sqltable.comment or "",
                )
                for key, sqltable in cast(
                    dict[str, AlchemyTable], the_db.AlchemyBase.metadata.tables
                ).items()
            ]

            modules.pop(db_id)
            return Response.ok(tables)
        except Exception as e:
            pprint(e)
            return Response.error(e)

    async def get_fields(self, db_id: str, table_id: str) -> Response[list[Field]]:
        try:
            the_db = import_module(db_id)
            db = DB(id=db_id, name="", description="")

            sqltable = cast(
                AlchemyTable,
                the_db.AlchemyBase.metadata.tables.get(table_id),
            )
            if sqltable is None:
                return Response.fail(f"Table {table_id} not found in DB {db_id}", 404)

            fields = [
                Field(
                    id=column.name,
                    name=column.name,
                    description=column.comment or "",
                    type=str(column.type),
                )
                for column in sqltable.columns
            ]

            modules.pop(db_id)
            return Response.ok(fields)
        except Exception as e:
            return Response.error(e)

    async def get_table(
        self, db_id: str, table_id: str, with_fields: bool = False
    ) -> Response[Table]:
        try:
            the_db = import_module(db_id)

            sqltable = cast(
                AlchemyTable,
                the_db.AlchemyBase.metadata.tables.get(table_id),
            )
            if sqltable is None:
                return Response.fail(f"Table {table_id} not found in DB {db_id}", 404)

            table = Table(
                id=sqltable.name,
                name=sqltable.fullname,
                description=sqltable.comment or "",
            )

            if with_fields:
                fields_response = await self.get_fields(db_id, table_id)
                if not fields_response.is_success:
                    return Response.fail(
                        f"Failed to get fields for table {table_id} in DB {db_id}: {fields_response.message}"
                    )
                if fields_response.payload is None:
                    return Response.fail(
                        f"No fields found for table {table_id} in DB {db_id}"
                    )
                table.fields = fields_response.payload

            if db_id in modules:
                modules.pop(db_id)
            return Response.ok(table)

        except Exception as e:
            return Response.error(e)

    async def get_db(
        self,
        db_id: str,
        with_tables: bool = False,
        with_fields: bool = False,
        with_kpis: bool = False,
        with_additional_info: bool = False,
    ) -> Response[DB]:
        try:
            pyfile_path = Path(self.definitions_path) / f"{db_id}.py"
            db = self._get_db_info(pyfile_path)
            if db is None:
                return Response.fail(f"DB {db_id} not found", 404)

            if with_tables:
                tables_response = await self.get_tables(db_id)
                if not tables_response.is_success:
                    return Response.fail(
                        f"Failed to get tables for DB {db_id}: {tables_response.message}"
                    )
                if tables_response.payload is None:
                    return Response.fail(f"No tables found for DB {db_id}")

                db.tables = tables_response.payload

                if with_fields:
                    for table in db.tables:
                        fields_response = await self.get_fields(db_id, table.id)
                        if not fields_response.is_success:
                            return Response.fail(
                                f"Failed to get fields for table {table.id} in DB {db_id}: {fields_response.message}"
                            )
                        if fields_response.payload is None:
                            return Response.fail(
                                f"No fields found for table {table.id} in DB {db_id}"
                            )
                        table.fields = fields_response.payload

            return Response.ok(db)

        except Exception as e:
            return Response.error(e)
