from __future__ import annotations
from typing import AsyncIterator, Optional, Sequence
from pprint import pprint, pformat
from traceback import format_exc, format_exception
from os import getenv
from asyncio import run, get_running_loop
from dotenv import load_dotenv
from pydantic import BaseModel
from sbilifeco.models.base import Response
from requests import Session
from functools import partial
from json import loads as json_loads
from re import compile, match

# Import other required contracts/modules here
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.boundaries.question_suggestion_flow import (
    IQuestionSuggestionFlow,
    QuestionSuggestionRequest,
    SuggestedQuestion,
)
from sbilifeco.cp.question_suggestion_flow.paths import Paths


class QuestionSuggestionHttpClient(HttpClient, IQuestionSuggestionFlow):
    def __init__(self):
        super().__init__()

    async def async_init(self, **kwargs) -> None: ...

    async def async_shutdown(self, **kwargs) -> None: ...

    async def suggest(
        self, req: QuestionSuggestionRequest
    ) -> Response[AsyncIterator[Sequence[SuggestedQuestion]]]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.BASE}"
            http_req = Request(url=url, method="GET", params=req.model_dump())
            pattern = compile(r"event: (.*)\ndata: (.*)\n\n")

            # Send request
            session = Session()
            res = await get_running_loop().run_in_executor(
                None, partial(session.send, http_req.prepare())
            )
            if not res.ok:
                return Response.fail(res.text, res.status_code)

            # Triage response
            async def __pick_stream():
                for chunk in res.iter_content(chunk_size=8192, decode_unicode=True):
                    if not chunk:
                        continue
                    try:
                        matches = pattern.match(chunk)
                        if not matches or len(matches.groups()) != 2:
                            print(
                                "Data from stream is not in expected format, skipping chunk."
                            )
                            continue

                        if matches.group(1) != "suggested_questions":
                            print(
                                f"Received event of type {matches.group(1)}, expected 'suggested_questions'. Skipping chunk."
                            )
                            continue

                        payload = json_loads(chunk)
                        questions = [
                            SuggestedQuestion.model_validate(item) for item in payload
                        ]
                        yield questions
                    except Exception as e:
                        print(f"Error in stream parsing: {e}")
                        print(format_exc())
                        continue

            # Return response
            return Response.ok(__pick_stream())
        except Exception as e:
            print(f"Error: {e}")
            print(format_exc())
            return Response.error(e)
        finally:
            ...
