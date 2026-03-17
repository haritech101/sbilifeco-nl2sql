from asyncio import run

from sbilifeco.sbin.db_schema_vectoriser import DbSchemaVectoriser
from os import getenv
from dotenv import load_dotenv
from sbilifeco.sbin.envvars import EnvVars, Defaults
from sbilifeco.cp.metadata_storage.http_client import MetadataStorageHttpClient
from sbilifeco.cp.vectoriser.http_client import VectoriserHttpClient
from sbilifeco.cp.vector_repo.http_client import VectorRepoHttpClient


class DBSchemaVectoriserService:
    async def start(self) -> None:
        load_dotenv()

        metadata_storage_proto = getenv(
            EnvVars.metadata_storage_proto, Defaults.metadata_storage_proto
        )
        metadata_storage_host = getenv(
            EnvVars.metadata_storage_host, Defaults.metadata_storage_host
        )
        metadata_storage_port = int(
            getenv(EnvVars.metadata_storage_port, Defaults.metadata_storage_port)
        )
        vectoriser_proto = getenv(EnvVars.vectoriser_proto, Defaults.vectoriser_proto)
        vectoriser_host = getenv(EnvVars.vectoriser_host, Defaults.vectoriser_host)
        vectoriser_port = int(getenv(EnvVars.vectoriser_port, Defaults.vectoriser_port))
        vector_repo_proto = getenv(
            EnvVars.vector_repo_proto, Defaults.vector_repo_proto
        )
        vector_repo_host = getenv(EnvVars.vector_repo_host, Defaults.vector_repo_host)
        vector_repo_port = int(
            getenv(EnvVars.vector_repo_port, Defaults.vector_repo_port)
        )
        db_id = getenv(EnvVars.db_id, "")

        self.metadata_storage = MetadataStorageHttpClient()
        (
            self.metadata_storage.set_proto(metadata_storage_proto)
            .set_host(metadata_storage_host)
            .set_port(metadata_storage_port)
        )

        self.vectoriser = VectoriserHttpClient()
        (
            self.vectoriser.set_proto(vectoriser_proto)
            .set_host(vectoriser_host)
            .set_port(vectoriser_port)
        )

        self.vector_repo = VectorRepoHttpClient()
        (
            self.vector_repo.set_proto(vector_repo_proto)
            .set_host(vector_repo_host)
            .set_port(vector_repo_port)
        )

        self.tool = (
            DbSchemaVectoriser()
            .set_metadata_storage(self.metadata_storage)
            .set_vectoriser(self.vectoriser)
            .set_vector_repo(self.vector_repo)
        )

        await self.tool.vectorise(db_id)


if __name__ == "__main__":
    run(DBSchemaVectoriserService().start())
