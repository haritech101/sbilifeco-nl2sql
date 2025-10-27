from __future__ import annotations
from json import loads
from typing import Any, Callable

from pydantic import BaseModel
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from psycopg import AsyncConnection
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB, KPI, Table, Field
from sbilifeco.cp.common.http.client import HttpClient
from requests import Request


class SynmetricApiCredentials(BaseModel):
    email: str
    password: str
    cookie: bool = False


class SynmetricApiResponse(BaseModel):
    jwt_token: str
    jwt_expires_in: int
    refresh_token: str


class Synmetrix(IMetadataStorage):
    CONN_STRING_TEMPLATE = "postgresql://{user}:{password}@{host}:{port}/{database}"
    DEFAULT_PG_PORT = 5432
    SQL_GET_DATASOURCES = "select id, name from datasources order by name"
    SQL_GET_SINGLE_DATASOURCE = "select id, name from datasources where id = %s"
    SQL_GET_ACTIVE_BRANCH = "select id from branches where datasource_id = %s and name = 'main' and status = 'active'"
    CUBE_META_PATH = "/api/v1/meta"

    def __init__(self) -> None:
        self.db_username = ""
        self.db_password = ""
        self.db_host = "localhost"
        self.db_port = self.DEFAULT_PG_PORT
        self.db_name = ""

        self.auth_proto = "http"
        self.auth_host = "localhost"
        self.auth_port = 0
        self.auth_path = ""
        self.auth_username = ""
        self.auth_password = ""

        self.cube_api_proto = "http"
        self.cube_api_host = "localhost"
        self.cube_api_port = 0

        self.conn: AsyncConnection | None = None
        self.api_jwt: str | None = None

        self.admin_api_proto = "http"
        self.admin_api_host = "localhost"
        self.admin_api_port = 80
        self.admin_api_base_path = "/"

    def set_db_username(self, username: str) -> Synmetrix:
        self.db_username = username
        return self

    def set_db_password(self, password: str) -> Synmetrix:
        self.db_password = password
        return self

    def set_db_host(self, host: str) -> Synmetrix:
        self.db_host = host
        return self

    def set_db_port(self, port: int) -> Synmetrix:
        self.db_port = port
        return self

    def set_db_name(self, db_name: str) -> Synmetrix:
        self.db_name = db_name
        return self

    def set_auth_proto(self, proto: str) -> Synmetrix:
        self.auth_proto = proto
        return self

    def set_auth_host(self, host: str) -> Synmetrix:
        self.auth_host = host
        return self

    def set_auth_port(self, port: int) -> Synmetrix:
        self.auth_port = port
        return self

    def set_auth_path(self, path: str) -> Synmetrix:
        self.auth_path = path
        return self

    def set_auth_username(self, username: str) -> Synmetrix:
        self.auth_username = username
        return self

    def set_auth_password(self, password: str) -> Synmetrix:
        self.auth_password = password
        return self

    def set_cube_api_proto(self, proto: str) -> Synmetrix:
        self.cube_api_proto = proto
        return self

    def set_cube_api_host(self, host: str) -> Synmetrix:
        self.cube_api_host = host
        return self

    def set_cube_api_port(self, port: int) -> Synmetrix:
        self.cube_api_port = port
        return self

    def set_admin_api_secret(self, secret: str) -> Synmetrix:
        self.admin_api_secret = secret
        return self

    def set_admin_api_username(self, username: str) -> Synmetrix:
        self.admin_api_username = username
        return self

    def set_admin_api_proto(self, proto: str) -> Synmetrix:
        self.admin_api_proto = proto
        return self

    def set_admin_api_host(self, host: str) -> Synmetrix:
        self.admin_api_host = host
        return self

    def set_admin_api_port(self, port: int) -> Synmetrix:
        self.admin_api_port = port
        return self

    def set_admin_api_base_path(self, path: str) -> Synmetrix:
        self.admin_api_base_path = path
        return self

    async def __with_db_connection(self, func: Callable | None, *args, **kwargs) -> Any:
        if self.conn is None:
            print(
                f"Connecting to Synmetrix database... psql://{self.db_username}@{self.db_host}:{self.db_port}/{self.db_name}"
            )

            conn_string = self.CONN_STRING_TEMPLATE.format(
                user=self.db_username,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
            )
            self.conn = await AsyncConnection.connect(conn_string)

        if func is not None:
            return await func(*args, **kwargs)

    async def __with_api_auth(self, func: Callable | None, *args, **kwargs) -> Any:
        if self.api_jwt is None:
            print(
                f"Authenticating with Synmetrix API {self.auth_proto}://{self.auth_host}:{self.auth_port}{self.auth_path}"
            )

            http_client = (
                HttpClient()
                .set_proto(self.auth_proto)
                .set_host(self.auth_host)
                .set_port(self.auth_port)
            )
            req = Request(
                method="POST",
                url=f"{http_client.url_base}{self.auth_path}",
                json=SynmetricApiCredentials(
                    email=self.auth_username, password=self.auth_password
                ).model_dump(),
            )

            response = await http_client.request_as_binary(req)
            if not response.is_success:
                raise Exception(
                    f"API authentication failed: {response.code} {response.message}"
                )

            assert response.payload is not None
            json_response = loads(response.payload.decode("utf-8"))
            synmetric_api_response = SynmetricApiResponse.model_validate(json_response)

            self.api_jwt = synmetric_api_response.jwt_token

        if func is not None:
            return await func(*args, **kwargs)

    async def __get_meta(self, db_id: str, branch_id: str) -> Response[dict[str, Any]]:
        async def _get_meta(db_id: str, branch_id: str) -> Response[dict[str, Any]]:
            assert self.api_jwt is not None

            print(
                f"Fetching metadata for database: {self.cube_api_proto}://{self.cube_api_host}:{self.cube_api_port}{self.CUBE_META_PATH}"
            )

            http_client = (
                HttpClient()
                .set_proto(self.cube_api_proto)
                .set_host(self.cube_api_host)
                .set_port(self.cube_api_port)
            )
            req = Request(
                method="GET",
                url=f"{http_client.url_base}{self.CUBE_META_PATH}",
                headers={
                    "x-hasura-datasource-id": db_id,
                    "x-hasura-branch-id": branch_id,
                    "Authorization": f"Bearer {self.api_jwt if self.api_jwt else ''}",
                },
            )
            response = await http_client.request_as_binary(req)

            if not response.is_success:
                return Response.fail(
                    f"Failed to fetch tables for database {db_id}: {response.message}",
                    response.code,
                )

            assert response.payload is not None

            return Response.ok(loads(response.payload.decode("utf-8")))

        return await self.__with_api_auth(_get_meta, db_id, branch_id)

    async def async_init(self) -> None:
        await self.__with_db_connection(None)

    async def async_shutdown(self) -> None:
        if self.conn:
            try:
                await self.conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

    async def get_dbs(self) -> Response[list[DB]]:
        async def _get_dbs() -> Response[list[DB]]:
            assert self.conn is not None

            print("Fetching list of databases from data source")

            async with self.conn.cursor() as cursor:
                await cursor.execute(self.SQL_GET_DATASOURCES)
                rows = await cursor.fetchall()
                return Response.ok([DB(id=str(row[0]), name=row[1]) for row in rows])

        try:
            return await self.__with_db_connection(_get_dbs)
        except Exception as e:
            print(f"Error fetching databases: {e}")
            return Response.error(e)

    async def get_db(
        self,
        db_id: str,
        with_tables: bool = False,
        with_fields: bool = False,
        with_kpis: bool = False,
        with_additional_info: bool = False,
    ) -> Response[DB]:
        async def _get_db_by_id() -> Response[DB]:
            assert self.conn is not None

            print(f"Fetching database with ID: {db_id} from data source")

            async with self.conn.cursor() as cursor:
                await cursor.execute(self.SQL_GET_SINGLE_DATASOURCE, [db_id])
                row = await cursor.fetchone()
                if row is None:
                    return Response.fail(f"Database with ID {db_id} not found", 404)

                return Response.ok(DB(id=str(row[0]), name=row[1]))

        try:
            db_response: Response[DB] = await self.__with_db_connection(_get_db_by_id)
            if not db_response.is_success:
                return Response.fail(db_response.message, db_response.code)
            db = db_response.payload

            assert db is not None

            if with_tables:
                tables_response = await self.get_tables(db_id)
                if not tables_response.is_success:
                    return Response.fail(tables_response.message, tables_response.code)

                db.tables = tables_response.payload

                assert db.tables is not None

                if not with_fields:
                    for table in db.tables:
                        table.fields = []

                # Additional logic to fetch fields, KPIs, etc. can be added here
                db.kpis = []
                db.additional_info = ""
                return Response.ok(db)
            else:
                return Response.fail(f"Database with ID {db_id} not found", 404)
        except Exception as e:
            print(f"Error fetching database with ID {db_id}: {e}")
            return Response.error(e)

    async def get_tables(self, db_id: str) -> Response[list[Table]]:
        async def _get_active_branch(db_id: str) -> str | None:
            assert self.conn is not None

            async with self.conn.cursor() as cursor:
                await cursor.execute(self.SQL_GET_ACTIVE_BRANCH, (db_id,))
                row = await cursor.fetchone()
                if row is None:
                    return None
                return str(row[0])

        try:
            active_branch_id = await self.__with_db_connection(
                _get_active_branch, db_id
            )
            if active_branch_id is None:
                return Response.fail(
                    f"No active branch found for database {db_id}", 404
                )

            meta_response: Response[Any] = await self.__get_meta(
                db_id, active_branch_id
            )
            if not meta_response.is_success:
                return Response.fail(
                    f"Failed to fetch metadata for database {db_id}: {meta_response.message}",
                    meta_response.code,
                )
            assert meta_response.payload is not None

            cubes = meta_response.payload.get("cubes", [])

            tables = [
                Table(
                    id=cube.get("name", ""),
                    name=cube.get("name", ""),
                    description=cube.get("description", ""),
                    fields=[
                        Field(
                            id=field.get("name", ""),
                            name=str(field.get("name", "")).split(".")[-1],
                            type=field.get("type", ""),
                            description=field.get("description", ""),
                            aka=field.get("meta", {}).get("aka", ""),
                        )
                        for field in (
                            cube.get("dimensions", []) + cube.get("measures", [])
                        )
                    ],
                )
                for cube in cubes
            ]

            return Response.ok(tables)
        except Exception as e:
            print(f"Error fetching tables for database {db_id}: {e}")
            return Response.error(e)

    async def upsert_db(self, db: DB) -> Response[str]:
        raise NotImplementedError(
            "Please use the dashboard for entry/edit of databases."
        )

    async def upsert_table(self, db_id, table: Table) -> Response[str]:
        raise NotImplementedError("Please use the dashboard for entry/edit of tables.")

    async def upsert_field(self, db_id, table_id, field: Field) -> Response[str]:
        raise NotImplementedError("Please use the dashboard for entry/edit of fields.")

    async def upsert_kpi(self, db_id: str, kpi: KPI) -> Response[str]:
        raise NotImplementedError("Please use the dashboard for entry/edit of KPIs.")

    async def delete_db(self, db_id: str) -> Response[None]:
        raise NotImplementedError("Please use the dashboard for deletion of databases.")

    async def delete_table(self, db_id: str, table_id: str) -> Response[None]:
        raise NotImplementedError("Please use the dashboard for deletion of tables.")

    async def delete_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[None]:
        raise NotImplementedError("Please use the dashboard for deletion of fields.")

    async def delete_kpi(self, db_id: str, kpi_id: str) -> Response[None]:
        raise NotImplementedError("Please use the dashboard for deletion of KPIs.")

    async def get_kpis(self, db_id: str) -> Response[list[KPI]]:
        raise NotImplementedError("KPIs are merged into fields in Synmetrix.")

    async def get_kpi(self, db_id: str, kpi_id: str) -> Response[KPI]:
        raise NotImplementedError("KPIs are merged into fields in Synmetrix.")

    async def get_table(
        self, db_id: str, table_id: str, with_fields: bool = False
    ) -> Response[Table]:
        raise NotImplementedError(
            "Single table retrieval is irrelevant in Synmetrix gateway since cubes return the entire schema hierarchy"
        )

    async def get_fields(self, db_id: str, table_id: str) -> Response[list[Field]]:
        raise NotImplementedError(
            "Fields retrieval is irrelevant in Synmetrix gateway since cubes return the entire schema hierarchy"
        )

    async def get_field(
        self, db_id: str, table_id: str, field_id: str
    ) -> Response[Field]:
        raise NotImplementedError(
            "Single field retrieval is irrelevant in Synmetrix gateway since cubes return the entire schema hierarchy"
        )

    async def _send_admin_api_request(self, graph_query: dict) -> Response[str]:
        req = Request()
        req.url = (
            f"{self.admin_api_proto}://"
            f"{self.admin_api_host}"
            f"{f":{self.admin_api_port}" if self.admin_api_port else ""}"
            f"{self.admin_api_base_path}"
        )
        req.method = "POST"
        req.headers = {
            "Content-Type": "application/json",
            "Hasura-Client-Name": self.admin_api_username,
            "x-hasura-admin-secret": self.admin_api_secret,
        }
        req.json = graph_query

        http_client = HttpClient()
        http_response = await http_client.request_as_binary(req)

        if not http_response.is_success:
            return Response.fail(http_response.message, http_response.code)
        elif not http_response.payload:
            return Response.fail("Admin API response is inexplicably empty", 500)

        return Response.ok(http_response.payload.decode("utf-8"))

    async def _get_data_sources(self) -> Response[list[dict[str, Any]]]:
        try:
            response = await self._send_admin_api_request(
                {"query": "query datasource { datasources { id name } }"}
            )
            return Response.ok([])
        except Exception as e:
            print(f"Error fetching data sources: {e}")
            return Response.error(e)
