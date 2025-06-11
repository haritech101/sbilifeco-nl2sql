from __future__ import annotations
from os import unlink
from pathlib import Path
from uuid import uuid4
from shutil import rmtree

from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, KPI, Table, Field
from sbilifeco.boundaries.metadata_storage import IMetadataStorage


class FSMetadataStorage(IMetadataStorage):
    def __init__(self):
        super().__init__()

    def set_metadata_path(self, metadata_path: str) -> FSMetadataStorage:
        self.metadata_path = metadata_path
        return self

    async def upsert_field(
        self, db_id: str, table_id: str, field: Field
    ) -> Response[str]:
        try:
            field.id = field.id or uuid4().hex

            field_path = f"{self.metadata_path}/{db_id}/{table_id}/{field.id}.json"

            with open(field_path, "w") as file:
                file.write(field.model_dump_json())

            return Response.ok(field.id)
        except Exception as e:
            return Response.error(e)

    async def delete_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[None]:
        try:
            field_path = f"{self.metadata_path}/{db_id}/{table_id}/{field_id}.json"
            unlink(field_path)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def get_fields(self, db_id: str, table_id: str) -> Response[list[Field]]:
        try:
            fields_path = f"{self.metadata_path}/{db_id}/{table_id}"
            fields: list[Field] = []
            for field_file in Path(fields_path).glob("*.json"):
                try:
                    with open(field_file, "r") as file:
                        field = Field.model_validate_json(file.read())
                        fields.append(field)
                except Exception as e:
                    continue  # Skip files that cannot be read

            fields.sort(key=lambda f: f.name)

            return Response.ok(fields)
        except Exception as e:
            return Response.error(e)

    async def get_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[Field]:
        try:
            field_path = f"{self.metadata_path}/{db_id}/{table_id}/{field_id}.json"
            try:
                with open(field_path, "r") as file:
                    field = Field.model_validate_json(file.read())
            except FileNotFoundError:
                return Response.fail("File not found", 404)
            return Response.ok(field)
        except Exception as e:
            return Response.error(e)

    async def upsert_table(self, db_id: str, table: Table) -> Response[str]:
        try:
            table.id = table.id or uuid4().hex

            table_path = f"{self.metadata_path}/{db_id}/{table.id}"
            Path(table_path).mkdir(exist_ok=True)

            with open(f"{table_path}/.name", "w") as file:
                file.write(table.name)
            with open(f"{table_path}/.description", "w") as file:
                file.write(table.description)

            return Response.ok(table.id)
        except Exception as e:
            return Response.error(e)

    async def delete_table(self, db_id: str, table_id: str) -> Response[None]:
        try:
            table_path = Path(f"{self.metadata_path}/{db_id}/{table_id}")
            if not table_path.exists():
                return Response.fail("Table not found", 404)

            rmtree(table_path)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def get_tables(self, db_id: str) -> Response[list[Table]]:
        try:
            tables_path = Path(f"{self.metadata_path}/{db_id}")
            if not tables_path.exists():
                return Response.fail("Database not found", 404)

            tables: list[Table] = []
            for table_dir in tables_path.iterdir():
                if table_dir.is_dir():
                    name = (table_dir / ".name").read_text().strip()
                    description = (table_dir / ".description").read_text().strip()
                    table_id = table_dir.name
                    tables.append(
                        Table(id=table_id, name=name, description=description)
                    )

            tables.sort(key=lambda t: t.name)
            return Response.ok(tables)
        except Exception as e:
            return Response.error(e)

    async def get_table(
        self, db_id: str, table_id: str, with_fields: bool = False
    ) -> Response[Table]:
        try:
            table_path = Path(f"{self.metadata_path}/{db_id}/{table_id}")
            if not table_path.exists():
                return Response.fail("Table not found", 404)

            name = (table_path / ".name").read_text().strip()
            description = (table_path / ".description").read_text().strip()

            table = Table(id=table_id, name=name, description=description)

            if with_fields:
                fields_response = await self.get_fields(db_id, table_id)
                if fields_response.is_success:
                    table.fields = fields_response.payload

            return Response.ok(table)
        except Exception as e:
            return Response.error(e)

    async def upsert_db(self, db: DB) -> Response[str]:
        try:
            db.id = db.id or uuid4().hex

            db_path = Path(f"{self.metadata_path}/{db.id}")
            db_path.mkdir(exist_ok=True)

            with open(db_path / ".name", "w") as file:
                file.write(db.name)
            with open(db_path / ".description", "w") as file:
                file.write(db.description)

            return Response.ok(db.id)
        except Exception as e:
            return Response.error(e)

    async def delete_db(self, db_id: str) -> Response[None]:
        try:
            db_path = Path(f"{self.metadata_path}/{db_id}")
            if not db_path.exists():
                return Response.fail("Database not found", 404)

            rmtree(db_path)
            return Response.ok(None)
        except Exception as e:
            return Response.error(e)

    async def get_dbs(self) -> Response[list[DB]]:
        try:
            dbs_path = Path(self.metadata_path)
            if not dbs_path.exists():
                return Response.fail("Metadata path does not exist", 404)

            dbs: list[DB] = []
            for db_dir in dbs_path.iterdir():
                if db_dir.is_dir() and (db_dir / ".name").exists():
                    name = (db_dir / ".name").read_text().strip()
                    description = (db_dir / ".description").read_text().strip()
                    db_id = db_dir.name
                    dbs.append(DB(id=db_id, name=name, description=description))

            dbs.sort(key=lambda d: d.name)
            return Response.ok(dbs)
        except Exception as e:
            return Response.error(e)

    async def get_db(
        self, db_id: str, with_tables: bool = False, with_fields: bool = False
    ) -> Response[DB]:
        try:
            db_path = Path(f"{self.metadata_path}/{db_id}")
            if not db_path.exists():
                return Response.fail("Database not found", 404)

            name = (db_path / ".name").read_text().strip()
            description = (db_path / ".description").read_text().strip()

            db = DB(id=db_id, name=name, description=description)

            if with_tables:
                tables_response = await self.get_tables(db_id)
                if tables_response.payload is not None:
                    db.tables = tables_response.payload
                    if with_fields:
                        for table in db.tables:
                            fields_response = await self.get_fields(db_id, table.id)
                            if fields_response.payload is not None:
                                table.fields = fields_response.payload

            return Response.ok(db)
        except Exception as e:
            return Response.error(e)

    async def upsert_kpi(self, db_id: str, kpi: KPI) -> Response[str]:
        try:
            db_path = Path(f"{self.metadata_path}/{db_id}")
            if not db_path.exists():
                return Response.fail(f"Database {db_id} not found", 404)

            kpi_path = db_path / f"{kpi.id}.json"
            kpi.id = kpi.id or uuid4().hex

            kpi_path.write_text(kpi.model_dump_json())

            return Response.ok(kpi.id)
        except Exception as e:
            print(e)
            return Response.error(e)

    async def delete_kpi(self, db_id: str, kpi_id: str) -> Response[None]:
        try:
            kpi_path = Path(f"{self.metadata_path}/{db_id}/{kpi_id}.json")
            if not kpi_path.exists():
                return Response.fail(f"KPI {kpi_id} not found", 404)

            unlink(kpi_path)
            return Response.ok(None)
        except Exception as e:
            print(e)
            return Response.error(e)

    async def get_kpis(self, db_id: str) -> Response[list[KPI]]:
        try:
            kpis_path = Path(f"{self.metadata_path}/{db_id}")
            if not kpis_path.exists():
                return Response.fail(f"Database {db_id} not found", 404)

            kpis: list[KPI] = []
            for kpi_file in kpis_path.glob("*.json"):
                try:
                    kpis.append(KPI.model_validate_json(kpi_file.read_text()))
                except Exception as e:
                    continue  # Skip files that cannot be read

            kpis.sort(key=lambda k: k.name)

            return Response.ok(kpis)
        except Exception as e:
            print(e)
            return Response.error(e)

    async def get_kpi(self, db_id: str, kpi_id: str) -> Response[KPI]:
        try:
            kpi_path = Path(f"{self.metadata_path}/{db_id}/{kpi_id}.json")
            if not kpi_path.exists():
                return Response.fail(f"KPI {kpi_id} not found", 404)

            return Response.ok(KPI.model_validate_json(kpi_path.read_text()))
        except Exception as e:
            print(e)
            return Response.error(e)
