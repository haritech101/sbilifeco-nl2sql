from __future__ import annotations

from asyncio import sleep
from functools import wraps
from json import loads as json_loads
from re import DOTALL, compile
from traceback import format_exc
from typing import Any, AsyncIterator, Sequence

# Import other required contracts/modules here
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.question_suggestion_flow import (
    IQuestionSuggestionFlow,
    QuestionSuggestionRequest,
    SuggestedQuestion,
)
from sbilifeco.models.base import Response
from yaml import dump as yaml_dump


def ensure_services(the_callable):
    @wraps(the_callable)
    async def the_one_called(
        self: QuestionSuggestionFlow, *args, **kwargs
    ) -> Response[Any]:
        if (
            not hasattr(self, "metadata_storage")
            or not hasattr(self, "llm")
            or not hasattr(self, "prompt_file")
            or not self.metadata_storage
            or not self.llm
            or not self.prompt_file
        ):
            error_msg = "Metadata storage, LLM services, and prompt file must be set before calling this method. Please use the setter methods to set these services."
            print(error_msg)
            return Response.fail(error_msg, 500)
        return await the_callable(self, *args, **kwargs)

    return the_one_called


class QuestionSuggestionFlow(IQuestionSuggestionFlow):
    def __init__(self):
        self.metadata_storage: IMetadataStorage
        self.llm: ILLM
        self.prompt_file: str

    def set_metadata_storage(
        self, metadata_storage: IMetadataStorage
    ) -> QuestionSuggestionFlow:
        self.metadata_storage = metadata_storage
        return self

    def set_llm(self, llm: ILLM) -> QuestionSuggestionFlow:
        self.llm = llm
        return self

    def set_prompt_file(self, prompt_file: str) -> QuestionSuggestionFlow:
        self.prompt_file = prompt_file
        return self

    async def async_init(self, **kwargs) -> None: ...

    async def async_shutdown(self, **kwargs) -> None: ...

    @ensure_services
    async def suggest(
        self, req: QuestionSuggestionRequest
    ) -> Response[AsyncIterator[Sequence[SuggestedQuestion]]]:
        try:
            # Database metadata
            print(f"Fetching metadata for DB ID {req.db_id}", flush=True)
            metadata_response = await self.metadata_storage.get_db(
                req.db_id, with_tables=True, with_fields=True
            )

            if not metadata_response.is_success:
                print(
                    f"Unable to fetch metadata for DB ID {req.db_id}: {metadata_response.message}"
                )
                return Response.fail(metadata_response.message, metadata_response.code)

            elif metadata_response.payload is None:
                message = f"Metadata for DB ID {req.db_id} is inexplicably empty"
                print(message)
                return Response.fail(message, 500)

            metadata_from_storage = metadata_response.payload

            # Metadata converted to YAML string to insert into LLM context
            metadata_as_context = yaml_dump(
                {
                    "name": metadata_from_storage.name,
                    "desc": metadata_from_storage.description,
                    "tables": [
                        {
                            "name": table.name,
                            "desc": table.description,
                            "fields": [
                                {
                                    "name": field.name,
                                    "type": field.type,
                                    "desc": field.description,
                                }
                                for field in (table.fields or [])
                            ],
                        }
                        for table in (metadata_from_storage.tables or [])
                    ],
                }
            )

            print(
                f"Fetched metadata for DB ID {req.db_id}:\n{metadata_as_context}",
                flush=True,
            )
            print(f"Reading prompt template from {self.prompt_file}", flush=True)
            with open(self.prompt_file, "r") as prompt_file:
                context_template = prompt_file.read()

            filled_context = context_template.format(
                db_metadata=metadata_as_context,
                num_suggestions=req.num_suggestions_per_batch,
            )
            print(f"{filled_context}", flush=True)

            async def __stream_questions() -> (
                AsyncIterator[Sequence[SuggestedQuestion]]
            ):
                pattern = compile(r"```json\s*(\{.*\})\s*```", flags=DOTALL)

                while True:
                    print(
                        f"Sending {len(filled_context)} characters to LLM", flush=True
                    )
                    llm_response = await self.llm.generate_reply(filled_context)

                    if not llm_response.is_success:
                        print(
                            f"Failure fetching reply from LLM: {llm_response.message}"
                        )
                        continue

                    elif llm_response.payload is None:
                        print("LLM response is inexplicably empty", flush=True)
                        continue

                    llm_reply = llm_response.payload

                    print(f"Received {len(llm_reply)} characters from LLM", flush=True)
                    try:
                        match = pattern.search(llm_reply)
                        if not match:
                            print(
                                "LLM response does not contain valid JSON in expected format",
                                flush=True,
                            )
                            continue

                        json_content = match.group(1)
                        yield [
                            SuggestedQuestion(question=item)
                            for item in json_loads(json_content).get("questions", [])
                        ]
                    except Exception as e:
                        print(f"Error parsing LLM response: {e}", flush=True)
                        continue

                    await sleep(req.interval_in_seconds)

            return Response.ok(__stream_questions())
        except Exception as e:
            print(f"Error while generating question suggestions: {e}")
            print(format_exc())
            return Response.error(e)
        finally:
            ...
