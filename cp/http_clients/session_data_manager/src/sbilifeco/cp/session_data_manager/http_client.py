from sbilifeco.cp.common.http.client import HttpClient
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.models.base import Response
from sbilifeco.cp.session_data_manager.paths import Paths, SessionData
from requests import Request


class SessionDataManagerHttpClient(HttpClient, ISessionDataManager):
    def __init__(self):
        HttpClient.__init__(self)

    async def update_session_data(self, session_id: str, data: str) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="POST",
                    url=f"{self.url_base}{Paths.SESSION_DATA_BY_ID.format(session_id=session_id)}",
                    json=SessionData(data=data).model_dump(),
                )
            )
        except Exception as e:
            return Response.error(e)

    async def get_session_data(self, session_id: str) -> Response[str]:
        try:
            return await self.request_as_model(
                Request(
                    method="GET",
                    url=f"{self.url_base}{Paths.SESSION_DATA_BY_ID.format(session_id=session_id)}",
                )
            )
        except Exception as e:
            return Response.error(e)

    async def delete_session_data(self, session_id: str) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="DELETE",
                    url=f"{self.url_base}{Paths.SESSION_DATA_BY_ID.format(session_id=session_id)}",
                )
            )
        except Exception as e:
            return Response.error(e)

    async def delete_all_session_data(self) -> Response[None]:
        try:
            return await self.request_as_model(
                Request(
                    method="DELETE",
                    url=f"{self.url_base}{Paths.BASE}",
                )
            )
        except Exception as e:
            return Response.error(e)
