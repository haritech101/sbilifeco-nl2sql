import sys

sys.path.append("./src")


from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.metadata_storage.microservice import MetadataStorageMicroservice
from sbilifeco.gateways.fs_metadata_storage import FSMetadataStorage
from sbilifeco.models.db_metadata import DB, Table, Field, KPI
from shutil import rmtree
from uuid import uuid4
from faker import Faker


class MetadataStorageHttpClientTest(IsolatedAsyncioTestCase):
    HTTP_PORT = 8181
    MD_PATH = ".local/.metadata"

    async def asyncSetUp(self):
        self.faker = Faker()
        self.storage = FSMetadataStorage().set_metadata_path(self.MD_PATH)
        self.microservice = MetadataStorageMicroservice().set_metadata_storage(
            self.storage
        )
        self.microservice.set_http_port(self.HTTP_PORT)
        await self.microservice.start()

        self.client = MetadataStorageHttpClient()
        (self.client.set_proto("http").set_host("localhost").set_port(self.HTTP_PORT))

        Path(self.MD_PATH).mkdir(parents=True, exist_ok=True)

    async def asyncTearDown(self):
        await self.microservice.stop()
        rmtree(self.MD_PATH, ignore_errors=True)

    def __generate_field(self) -> Field:
        return Field(
            id=uuid4().hex,
            name=self.faker.word(),
            type=self.faker.word(),
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
        return Table(
            id=uuid4().hex,
            name=self.faker.word(),
            description=self.faker.sentence(),
            fields=[self.__generate_field() for _ in range(3)],
        )

    def __generate_db(self) -> DB:
        db = DB(
            id=uuid4().hex,
            name=self.faker.company(),
            description=self.faker.sentence(),
            tables=[self.__generate_table() for _ in range(2)],
            kpis=[self.__generate_kpi() for _ in range(5)],
        )
        return db

    async def test_upsert_db(self) -> None:
        # Arrange
        db = self.__generate_db()

        # Act
        upsert_response = await self.client.upsert_db(db)
        assert db.tables is not None
        db.tables.sort(key=lambda t: t.name)
        for table in db.tables:
            upsert_response = await self.client.upsert_table(db.id, table)
            assert table.fields is not None
            table.fields.sort(key=lambda f: f.name)
            for field in table.fields:
                upsert_response = await self.client.upsert_field(db.id, table.id, field)

        assert db.kpis is not None
        db.kpis.sort(key=lambda k: k.name)
        for kpi in db.kpis:
            upsert_response = await self.client.upsert_kpi(db.id, kpi)

        # Assert
        fetch_response = await self.client.get_db(
            db.id, with_tables=True, with_fields=True, with_kpis=True
        )
        self.assertTrue(fetch_response.is_success, fetch_response.message)
        self.assertEqual(fetch_response.payload, db)

    async def test_delete_db(self) -> None:
        # Arrange
        db = self.__generate_db()
        await self.client.upsert_db(db)

        # Act
        delete_response = await self.client.delete_db(db.id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)
        fetch_response = await self.client.get_db(db.id)
        self.assertFalse(fetch_response.is_success, "DB should be deleted")

    async def test_get_dbs(self) -> None:
        # Arrange
        dbs = [self.__generate_db() for _ in range(3)]
        for db in dbs:
            await self.client.upsert_db(db)

        for db in dbs:
            db.tables = None  # We are not testing tables here
            db.kpis = None  # We are not testing KPIs here

        dbs.sort(key=lambda d: d.name)

        # Act
        response = await self.client.get_dbs()

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, dbs)

    async def test_delete_table(self) -> None:
        # Arrange
        db_id = uuid4().hex
        (Path(self.MD_PATH) / db_id).mkdir(parents=True, exist_ok=True)

        table = self.__generate_table()
        await self.client.upsert_table(db_id, table)

        # Act
        delete_response = await self.client.delete_table(db_id, table.id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)
        fetch_response = await self.client.get_table(db_id, table.id)
        self.assertFalse(fetch_response.is_success, "Table should be deleted")

    async def test_get_tables(self) -> None:
        # Arrange
        db_id = uuid4().hex
        (Path(self.MD_PATH) / db_id).mkdir(parents=True, exist_ok=True)

        tables = [self.__generate_table() for _ in range(3)]
        for table in tables:
            table.fields = None  # We are not testing fields here
            await self.client.upsert_table(db_id, table)

        tables.sort(key=lambda t: t.name)

        # Act
        response = await self.client.get_tables(db_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, tables)

    async def test_get_table_with_flags(self) -> None:
        # Arrange
        db_id = uuid4().hex
        (Path(self.MD_PATH) / db_id).mkdir(parents=True, exist_ok=True)

        table = self.__generate_table()
        await self.client.upsert_table(db_id, table)
        assert table.fields is not None
        for field in table.fields:
            await self.client.upsert_field(db_id, table.id, field)
        table.fields.sort(key=lambda f: f.name)

        # Act
        response = await self.client.get_table(db_id, table.id, with_fields=True)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, table)

    async def test_delete_field(self) -> None:
        # Arrange
        db_id = uuid4().hex
        table_id = uuid4().hex
        (Path(self.MD_PATH) / db_id / table_id).mkdir(parents=True, exist_ok=True)

        field = self.__generate_field()
        await self.client.upsert_field(db_id, table_id, field)

        # Act
        delete_response = await self.client.delete_field(db_id, table_id, field.id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)
        fetch_response = await self.client.get_field(db_id, table_id, field.id)
        self.assertFalse(fetch_response.is_success, "Field should be deleted")
        self.assertEqual(fetch_response.code, 404, "Field should not exist")

    async def test_get_fields(self) -> None:
        # Arrange
        db_id = uuid4().hex
        table_id = uuid4().hex
        (Path(self.MD_PATH) / db_id / table_id).mkdir(parents=True, exist_ok=True)

        fields = [self.__generate_field() for _ in range(3)]
        for field in fields:
            await self.client.upsert_field(db_id, table_id, field)

        fields.sort(key=lambda f: f.name)

        # Act
        response = await self.client.get_fields(db_id, table_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, fields)

    async def test_delete_kpi(self) -> None:
        # Arrange
        db_id = uuid4().hex
        (Path(self.MD_PATH) / db_id).mkdir(parents=True, exist_ok=True)

        kpi = self.__generate_kpi()
        await self.client.upsert_kpi(db_id, kpi)

        # Act
        delete_response = await self.client.delete_kpi(db_id, kpi.id)

        # Assert
        self.assertTrue(delete_response.is_success, delete_response.message)
        fetch_response = await self.client.get_kpi(db_id, kpi.id)
        self.assertFalse(fetch_response.is_success, "KPI should be deleted")
        self.assertEqual(fetch_response.code, 404, "KPI should not exist")

    async def test_get_kpis(self) -> None:
        # Arrange
        db_id = uuid4().hex
        (Path(self.MD_PATH) / db_id).mkdir(parents=True, exist_ok=True)

        kpis = [self.__generate_kpi() for _ in range(3)]
        for kpi in kpis:
            await self.client.upsert_kpi(db_id, kpi)

        kpis.sort(key=lambda k: k.name)

        # Act
        response = await self.client.get_kpis(db_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        self.assertEqual(response.payload, kpis)
