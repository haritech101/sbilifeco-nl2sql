from collections.abc import AsyncIterator
from traceback import format_exc
from functools import partial
from asyncio import get_running_loop

from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.query_flow import IQueryFlow, QueryFlowRequest
from sbilifeco.models.base import Response
from requests import Request, Session
from sbilifeco.cp.query_flow.paths import Paths, QueryRequest


class QueryFlowHttpClient(HttpClient, IQueryFlow):
    def __init__(self) -> None:
        HttpClient.__init__(self)

    async def start_session(self) -> Response[str]:
        try:
            return await self.request_as_model(
                Request(method="POST", url=f"{self.url_base}{Paths.SESSIONS}", json={})
            )
        except Exception as e:
            return Response.error(e)

    async def stop_session(self, session_id: str) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="DELETE",
                    url=f"{self.url_base}{Paths.SESSION_BY_ID.format(session_id=session_id)}",
                )
            )
        except Exception as e:
            return Response.error(e)

    async def reset_session(self, session_id: str) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.SESSION_RESET.format(session_id=session_id)}",
                    json={},
                )
            )
        except Exception as e:
            return Response.error(e)

    async def query(
        self,
        dbId: str,
        session_id: str,
        question: str,
        is_pii_allowed: bool = False,
        with_thoughts: bool = False,
    ) -> Response[str]:
        try:
            req = Request(
                method="POST",
                url=f"{self.url_base}{Paths.QUERIES.format(session_id=session_id)}",
                json=QueryRequest(
                    db_id=dbId,
                    question=question,
                    is_pii_allowed=is_pii_allowed,
                    with_thoughts=with_thoughts,
                ).model_dump(),
            )
            return await self.request_as_model(req)
        except Exception as e:
            return Response.error(e)

    async def ask(
        self, query_flow_request: QueryFlowRequest
    ) -> Response[AsyncIterator[str]]:
        try:
            # Form request
            url = f"{self.url_base}{Paths.ASKS}"
            req = Request(url=url, method="POST", json=query_flow_request.model_dump())

            # Send request
            with Session() as session:
                res = await get_running_loop().run_in_executor(
                    None,
                    partial(session.send, session.prepare_request(req), stream=True),
                )

            # Triage response
            async def stream_content() -> AsyncIterator[str]:
                for chunk in res.iter_content(chunk_size=4096, decode_unicode=True):
                    try:
                        yield chunk
                    except Exception as e:
                        print(f"Error in streaming response: {e}")
                        print(format_exc())
                        continue

            # Return response
            return Response.ok(stream_content())
        except Exception as e:
            print(f"Error: {e}")
            print(format_exc())
            return Response.error(e)
        finally:
            ...
