import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from sbilifeco.gateways.synmetrix import Synmetrix
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.metadata_storage.microservice import MetadataStorageMicroservice
from dotenv import load_dotenv
from os import getenv

from .envvars import EnvVars, Defaults


class ClientWithSynmetrixTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        self.test_environment = getenv(
            EnvVars.test_environment, Defaults.test_environment
        )

        if self.test_environment == "local":
            db_host = getenv(EnvVars.db_host, Defaults.db_host)
            db_port = int(getenv(EnvVars.db_port, Defaults.db_port))
            db_username = getenv(EnvVars.db_username, Defaults.db_username)
            db_password = getenv(EnvVars.db_password, Defaults.db_password)
            db_name = getenv(EnvVars.db_name, Defaults.db_name)
            auth_port = int(getenv(EnvVars.auth_port, Defaults.auth_port))
            auth_username = getenv(EnvVars.auth_username, Defaults.auth_username)
            auth_password = getenv(EnvVars.auth_password, Defaults.auth_password)
            auth_path = getenv(EnvVars.auth_path, Defaults.auth_path)
            cube_port = int(getenv(EnvVars.cube_port, Defaults.cube_port))

            self.gateway = Synmetrix()
            (
                self.gateway.set_db_host(db_host)
                .set_db_port(db_port)
                .set_db_username(db_username)
                .set_db_password(db_password)
                .set_db_name(db_name)
                .set_auth_port(auth_port)
                .set_auth_username(auth_username)
                .set_auth_password(auth_password)
                .set_auth_path(auth_path)
                .set_cube_api_port(cube_port)
            )

            microservice_proto = getenv(
                EnvVars.microservice_proto, Defaults.microservice_proto
            )
            microservice_host = getenv(
                EnvVars.microservice_host, Defaults.microservice_host
            )
            microservice_port = int(
                getenv(
                    EnvVars.local_microservice_port, Defaults.local_microservice_port
                )
            )

            self.microservice = MetadataStorageMicroservice()
            self.microservice.set_metadata_storage(self.gateway).set_http_port(
                microservice_port
            )

            await self.microservice.start()
        else:
            microservice_proto = getenv(
                EnvVars.microservice_proto, Defaults.microservice_proto
            )
            microservice_host = getenv(
                EnvVars.microservice_host, Defaults.microservice_host
            )
            microservice_port = int(
                getenv(
                    EnvVars.remote_microservice_port, Defaults.remote_microservice_port
                )
            )

        self.client = MetadataStorageHttpClient()
        self.client.set_proto(microservice_proto).set_host(microservice_host).set_port(
            microservice_port
        )

    async def asyncTearDown(self) -> None:
        if self.test_environment == "local":
            await self.microservice.stop()

    async def test_get_dbs(self) -> None:
        # Arrange

        # Act
        dbs_response = await self.client.get_dbs()

        # Assert
        self.assertTrue(dbs_response.is_success, dbs_response.message)
        assert dbs_response.payload, "No databases found"
        for db in dbs_response.payload:
            self.assertTrue(db.name, "Database name is empty")
            self.assertTrue(db.id, "Database ID is empty")

    async def test_get_db(self) -> None:
        # Arrange
        test_id = "325d08cc-950f-4759-acc3-2d41a8b604fa"

        # Act
        db_response = await self.client.get_db(
            test_id, with_tables=True, with_fields=True
        )

        # Assert
        self.assertTrue(db_response.is_success, db_response.message)
        assert db_response.payload, "Database not found"
        self.assertTrue(db_response.payload.name, "Database name is empty")
        self.assertTrue(db_response.payload.id, "Database ID is empty")
        assert db_response.payload.tables, "No tables found in the database"
        for table in db_response.payload.tables:
            self.assertTrue(table.name, "Table name is empty")
            self.assertTrue(table.id, "Table ID is empty")
            self.assertTrue(table.description, "Table description is empty")

            assert table.fields, "No fields found in the table"
            for field in table.fields:
                self.assertTrue(field.name, "Field name is empty")
                self.assertTrue(field.id, "Field ID is empty")
                self.assertTrue(field.type, "Field type is empty")
                # self.assertTrue(field.description, "Field description is empty")
