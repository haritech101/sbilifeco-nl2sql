import sys, os

sys.path.append("./src")

from pathlib import Path
from shutil import rmtree
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from faker import Faker

from sbilifeco.gateways.fs_metadata_storage import FSMetadataStorage
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, Field, Table, KPI


class FSMetadataStorageTest(IsolatedAsyncioTestCase):
    PATH = "./.local/.metadata"

    async def asyncSetUp(self) -> None:
        self.gateway = FSMetadataStorage().set_metadata_path(self.PATH)
        self.faker = Faker()

    async def asyncTearDown(self) -> None:
        try:
            rmtree(self.PATH)
        except FileNotFoundError:
            pass

    def __generate_field(self) -> Field:
        return Field(
            id=uuid4().hex,
            name=self.faker.word(),
            description=self.faker.sentence(),
        )

    def __generate_kpi(self) -> KPI:
        return KPI(
            id=uuid4().hex,
            name=self.faker.word(),
            aka=self.faker.word(),
            description=self.faker.sentence(),
            formula=self.faker.sentence(),
        )

    def __generate_table(self) -> Table:
        tables = Table(
            id=uuid4().hex,
            name=self.faker.word(),
            description=self.faker.sentence(),
            fields=[self.__generate_field() for _ in range(3)],
        )

        assert tables.fields is not None, "Table must have at least one field"
        tables.fields.sort(key=lambda f: f.name)

        return tables

    def __generate_db(self) -> DB:
        db = DB(
            id=uuid4().hex,
            name=self.faker.word(),
            description=self.faker.sentence(),
            tables=[self.__generate_table() for _ in range(3)],
            kpis=[self.__generate_kpi() for _ in range(6)],
            additional_info=self.faker.paragraph(),
        )

        assert db.tables is not None, "DB must have at least one table"
        db.tables.sort(key=lambda t: t.name)

        return db

    async def test_upsert_field(self) -> None:
        # Arrange
        db_id = uuid4().hex
        table_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}/{table_id}").mkdir(parents=True, exist_ok=True)

        field = self.__generate_field()

        # Act
        response: Response[str] = await self.gateway.upsert_field(
            db_id, table_id, field
        )

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, field.id)

        field_response = await self.gateway.get_field(db_id, table_id, field.id)
        self.assertTrue(field_response.is_success, field_response.message)
        self.assertEqual(field_response.payload, field)

    async def test_delete_field(self) -> None:
        # Arrange
        db_id = uuid4().hex
        table_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}/{table_id}").mkdir(parents=True, exist_ok=True)

        field = self.__generate_field()
        await self.gateway.upsert_field(db_id, table_id, field)

        # Act
        response: Response[None] = await self.gateway.delete_field(
            db_id, table_id, field.id
        )

        # Assert
        self.assertTrue(response.is_success, response.message)

        field_response = await self.gateway.get_field(db_id, table_id, field.id)
        self.assertFalse(field_response.is_success, "Field should have been deleted")
        self.assertEqual(field_response.code, 404, "Field should not be found")

    async def test_get_fields(self) -> None:
        # Arrange
        db_id = uuid4().hex
        table_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}/{table_id}").mkdir(parents=True, exist_ok=True)

        fields = [self.__generate_field() for _ in range(3)]
        for field in fields:
            await self.gateway.upsert_field(db_id, table_id, field)

        # Act
        response: Response[list[Field]] = await self.gateway.get_fields(db_id, table_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Payload is None"
        for field in fields:
            self.assertIn(field, response.payload)

    async def test_upsert_table(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)

        table = self.__generate_table()
        table.fields = None

        # Act
        response: Response[str] = await self.gateway.upsert_table(db_id, table)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, table.id)

        table_response = await self.gateway.get_table(
            db_id, table.id, with_fields=False
        )
        self.assertTrue(table_response.is_success, table_response.message)
        self.assertEqual(table_response.payload, table)

    async def test_delete_table(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)

        table = self.__generate_table()
        await self.gateway.upsert_table(db_id, table)

        # Act
        response: Response[None] = await self.gateway.delete_table(db_id, table.id)

        # Assert
        self.assertTrue(response.is_success, response.message)

        table_response = await self.gateway.get_table(db_id, table.id)
        self.assertFalse(table_response.is_success, "Table should have been deleted")
        self.assertEqual(table_response.code, 404, "Table should not be found")

    async def test_get_table_with_fields(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)

        table = self.__generate_table()
        await self.gateway.upsert_table(db_id, table)

        assert table.fields is not None, "Table must have at least one field"
        for field in table.fields:
            await self.gateway.upsert_field(db_id, table.id, field)

        # Act
        response: Response[Table] = await self.gateway.get_table(
            db_id, table.id, with_fields=True
        )

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, table)

    async def test_get_tables(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)

        tables = [self.__generate_table() for _ in range(3)]
        for table in tables:
            table.fields = None  # Ensure fields are not included
            await self.gateway.upsert_table(db_id, table)

        # Act
        response: Response[list[Table]] = await self.gateway.get_tables(db_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Payload is None"
        for table in tables:
            self.assertIn(table, response.payload)

    async def test_upsert_db(self) -> None:
        # Arrange
        Path(self.PATH).mkdir(parents=True, exist_ok=True)

        db = self.__generate_db()
        db.tables = None
        db.kpis = None
        db.additional_info = None

        # Act
        response: Response[str] = await self.gateway.upsert_db(db)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, db.id)

        db_response = await self.gateway.get_db(db.id)
        self.assertTrue(db_response.is_success, db_response.message)
        self.assertEqual(db_response.payload, db)

    async def test_delete_db(self) -> None:
        # Arrange
        Path(self.PATH).mkdir(parents=True, exist_ok=True)

        db = self.__generate_db()
        await self.gateway.upsert_db(db)

        # Act
        response: Response[None] = await self.gateway.delete_db(db.id)

        # Assert
        self.assertTrue(response.is_success, response.message)

        db_response = await self.gateway.get_db(db.id)
        self.assertFalse(db_response.is_success, "DB should have been deleted")
        self.assertEqual(db_response.code, 404, "DB should not be found")

    async def test_get_db_with_components(self) -> None:
        # Arrange
        Path(self.PATH).mkdir(parents=True, exist_ok=True)

        db = self.__generate_db()
        await self.gateway.upsert_db(db)

        assert db.tables is not None, "DB must have at least one table"
        db.tables.sort(key=lambda t: t.name)
        for table in db.tables:
            await self.gateway.upsert_table(db.id, table)
            assert table.fields is not None, "Table must have at least one field"
            table.fields.sort(key=lambda f: f.name)
            for field in table.fields:
                await self.gateway.upsert_field(db.id, table.id, field)

        assert db.kpis is not None, "DB must have at least one KPI"
        db.kpis.sort(key=lambda k: k.name)
        for kpi in db.kpis:
            await self.gateway.upsert_kpi(db.id, kpi)

        # Act
        response: Response[DB] = await self.gateway.get_db(
            db.id,
            with_tables=True,
            with_fields=True,
            with_kpis=True,
            with_additional_info=True,
        )

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, db)

    async def test_get_dbs(self) -> None:
        # Arrange
        Path(self.PATH).mkdir(parents=True, exist_ok=True)

        dbs = [self.__generate_db() for _ in range(3)]
        for db in dbs:
            db.tables = None
            db.kpis = None
            db.additional_info = None
            await self.gateway.upsert_db(db)

        # Act
        response: Response[list[DB]] = await self.gateway.get_dbs()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Payload is None"
        for db in dbs:
            self.assertIn(db, response.payload)

    async def test_upsert_kpi(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)

        kpi = KPI(
            id=uuid4().hex,
            name=self.faker.word(),
            aka=self.faker.word(),
            description=self.faker.sentence(),
            formula=self.faker.sentence(),
        )

        # Act
        response: Response[str] = await self.gateway.upsert_kpi(db_id, kpi)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, kpi.id)

        kpi_response = await self.gateway.get_kpi(db_id, kpi.id)
        self.assertTrue(kpi_response.is_success, kpi_response.message)
        self.assertEqual(kpi_response.payload, kpi)

    async def test_delete_kpi(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)

        kpi = KPI(
            id=uuid4().hex,
            name=self.faker.word(),
            aka=self.faker.word(),
            description=self.faker.sentence(),
            formula=self.faker.sentence(),
        )
        await self.gateway.upsert_kpi(db_id, kpi)
        assert kpi.id is not None, "KPI must have an ID"

        # Act
        response: Response[None] = await self.gateway.delete_kpi(db_id, kpi.id)

        # Assert
        self.assertTrue(response.is_success, response.message)

        kpi_response = await self.gateway.get_kpi(db_id, kpi.id)
        self.assertFalse(kpi_response.is_success, kpi_response.message)
        self.assertEqual(kpi_response.code, 404, "KPI should not be found")

    async def test_get_kpis(self) -> None:
        # Arrange
        db_id = uuid4().hex
        Path(f"{self.PATH}/{db_id}").mkdir(parents=True, exist_ok=True)
        other_db_id = uuid4().hex
        Path(f"{self.PATH}/{other_db_id}").mkdir(parents=True, exist_ok=True)

        kpis = [
            KPI(
                id=uuid4().hex,
                name=self.faker.word(),
                aka=self.faker.word(),
                description=self.faker.sentence(),
                formula=self.faker.sentence(),
            )
            for _ in range(3)
        ]
        for kpi in kpis:
            await self.gateway.upsert_kpi(db_id, kpi)

        # Act
        response: Response[list[KPI]] = await self.gateway.get_kpis(db_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Payload is None"
        for kpi in kpis:
            self.assertIn(kpi, response.payload)

        # Act
        response: Response[list[KPI]] = await self.gateway.get_kpis(other_db_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None, "Payload is None"
        self.assertEqual(response.payload, [])
