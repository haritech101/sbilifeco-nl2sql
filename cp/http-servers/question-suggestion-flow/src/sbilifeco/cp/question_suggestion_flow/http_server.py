from __future__ import annotations

from json import dumps as json_dumps
from traceback import format_exc
from typing import Annotated

from fastapi.param_functions import Query
from fastapi.responses import PlainTextResponse, StreamingResponse
from sbilifeco.boundaries.question_suggestion_flow import (
    IQuestionSuggestionFlow,
    QuestionSuggestionRequest,
)

# Import other required contracts/modules here
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.question_suggestion_flow.paths import Paths


class QuestionSuggestionHttpServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.question_suggestion_flow: IQuestionSuggestionFlow

    def set_question_suggestion_flow(
        self, flow: IQuestionSuggestionFlow
    ) -> QuestionSuggestionHttpServer:
        self.question_suggestion_flow = flow
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.get(Paths.BASE)
        async def suggest(
            req: Annotated[QuestionSuggestionRequest, Query()],
        ):
            try:
                suggestion_response = await self.question_suggestion_flow.suggest(req)

                if not suggestion_response.is_success:
                    print(
                        f"Failure generating question suggestions: {suggestion_response.message}"
                    )
                    return PlainTextResponse(
                        content=suggestion_response.message,
                        status_code=suggestion_response.code,
                    )

                elif suggestion_response.payload is None:
                    message = "Payload is inexplicably empty"
                    print(message)
                    return PlainTextResponse(content=message, status_code=500)

                stream = suggestion_response.payload

                async def stream_as_events():
                    async for suggestions in stream:
                        print(
                            "Received list of suggestions from flow, yielding to HTTP client as an event stream event",
                            flush=True,
                        )
                        yield f"event: suggestion\ndata: {json_dumps([suggestion.model_dump() for suggestion in suggestions])}\n\n"

                return StreamingResponse(
                    stream_as_events(), media_type="text/event-stream"
                )

            except Exception as e:
                print(f"Error in suggest endpoint: {e}")
                print(format_exc())
                return PlainTextResponse(content=format_exc(), status_code=500)
