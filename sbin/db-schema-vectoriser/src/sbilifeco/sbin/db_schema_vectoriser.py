from __future__ import annotations

from traceback import format_exc
from uuid import uuid4

from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.vector_repo import BaseVectorRepo
from sbilifeco.boundaries.vectoriser import BaseVectoriser
from sbilifeco.models.vectorisation import VectorisedRecord, RecordMetadata


class DbSchemaVectoriser:
    def __init__(self) -> None:
        self.metadata_storage: IMetadataStorage

    def set_metadata_storage(
        self, metadata_storage: IMetadataStorage
    ) -> DbSchemaVectoriser:
        self.metadata_storage = metadata_storage
        return self

    def set_vectoriser(self, vectoriser: BaseVectoriser) -> DbSchemaVectoriser:
        self.vectoriser = vectoriser
        return self

    def set_vector_repo(self, vector_repo: BaseVectorRepo) -> DbSchemaVectoriser:
        self.vector_repo = vector_repo
        return self

    async def async_init(self) -> None: ...

    async def async_shutdown(self) -> None: ...

    async def vectorise(self, schema: str) -> None:
        try:
            print("Fetch DB metadata for the given schema")
            metadata_response = await self.metadata_storage.get_db(
                db_id=schema, with_tables=True, with_fields=True
            )

            if not metadata_response.is_success:
                print(f"Failure: {metadata_response.message}")
                return

            elif metadata_response.payload is None:
                message = "Payload is inexplicably empty"
                print(message)
                return

            metadata = metadata_response.payload
            if metadata.tables:
                for table in metadata.tables:
                    if table.fields:
                        for field in table.fields:
                            print(
                                f"Stringifying and vectorising field {metadata.id}/{table.id}/{field.id}"
                            )
                            stringified_field = field.model_dump_json()

                            vector_response = await self.vectoriser.vectorise(
                                uuid4().hex, stringified_field
                            )

                            if not vector_response.is_success:
                                print(
                                    f"Failure generating vector for {metadata.id}/{table.id}/{field.id}: {vector_response.message}"
                                )
                                continue

                            elif vector_response.payload is None:
                                message = f"Generated vector for {metadata.id}/{table.id}/{field.id} is inexplicably empty"
                                print(message)
                                continue

                            field_vector = vector_response.payload

                            record = VectorisedRecord(
                                id=uuid4().hex,
                                document=stringified_field,
                                vector=field_vector,
                                metadata=RecordMetadata(
                                    source_id=metadata.id,
                                    source=f"{metadata.id}/{table.id}/{field.id}",
                                ),
                            )
                            print(record)
                            vectorisation_response = await self.vector_repo.crupdate(
                                record
                            )
                            if not vectorisation_response.is_success:
                                print(
                                    f"Failure saving vector for {table.id}/{field.id}: {vectorisation_response.message}"
                                )

                    table.fields = []

                    print(f"Stringifying and vectorising table {table.id}")
                    stringified_table = table.model_dump_json()

                    vector_response = await self.vectoriser.vectorise(
                        uuid4().hex, stringified_table
                    )
                    if not vector_response.is_success:
                        print(f"Failure generating vector: {vector_response.message}")
                        continue

                    elif vector_response.payload is None:
                        message = f"Generated vector for {metadata.id}/{table.id} is inexplicably empty"
                        print(message)
                        continue

                    table_vector = vector_response.payload
                    record = VectorisedRecord(
                        id=uuid4().hex,
                        document=stringified_table,
                        vector=table_vector,
                        metadata=RecordMetadata(
                            source_id=metadata.id, source=f"{metadata.id}/{table.id}"
                        ),
                    )
                    vectorisation_response = await self.vector_repo.crupdate(record)
                    if not vectorisation_response.is_success:
                        print(
                            f"Failure saving vector for {metadata.id}/{table.id}: {vectorisation_response.message}"
                        )
        except Exception as e:
            print(f"Error: {e}")
            print(format_exc())
        finally:
            ...
