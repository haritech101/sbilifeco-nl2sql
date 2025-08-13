from __future__ import annotations
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.models.base import Response
from sbilifeco.cp.session_data_manager.paths import Paths, SessionData


class SessionDataManagerHttpServer(HttpServer):
    def __init__(self):
        HttpServer.__init__(self)
        self.session_data_manager: ISessionDataManager

    def set_session_data_manager(
        self, session_data_manager: ISessionDataManager
    ) -> SessionDataManagerHttpServer:
        self.session_data_manager = session_data_manager
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.post(Paths.SESSION_DATA_BY_ID)
        async def update_session_data(
            session_id: str, session_data: SessionData
        ) -> Response[None]:
            try:
                return await self.session_data_manager.update_session_data(
                    session_id, session_data.data
                )
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.SESSION_DATA_BY_ID)
        async def delete_session_data(session_id: str) -> Response[None]:
            try:
                return await self.session_data_manager.delete_session_data(session_id)
            except Exception as e:
                return Response.error(e)

        @self.delete(Paths.BASE)
        async def delete_all_session_data() -> Response[None]:
            try:
                return await self.session_data_manager.delete_all_session_data()
            except Exception as e:
                return Response.error(e)

        @self.get(Paths.SESSION_DATA_BY_ID)
        async def get_session_data(session_id: str) -> Response[str]:
            try:
                return await self.session_data_manager.get_session_data(session_id)
            except Exception as e:
                return Response.error(e)
