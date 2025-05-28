from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn import Config, Server


class HttpServer(FastAPI):
    def __init__(self) -> None:
        super().__init__()
        self.log_level: str = "info"
        self.http_port: int = 80
        self.bound_host: str = "0.0.0.0"
        self.allowed_origins: list[str] = ["*"]
        self.are_credentials_allowed: bool = True
        self.allowed_methods: list[str] = ["*"]
        self.allowed_headers: list[str] = ["*"]
        self.allowed_hosts: list[str] = ["*"]
        self.allowed_forwarded_hosts: list[str] = ["*"]

    def set_log_level(self, log_level: str) -> HttpServer:
        self.log_level = log_level
        return self

    def set_http_port(self, http_port: int) -> HttpServer:
        self.http_port = http_port
        return self

    def set_bound_host(self, bound_host: str) -> HttpServer:
        self.bound_host = bound_host
        return self

    def set_allowed_origins(self, allowed_origins: list[str]) -> HttpServer:
        self.allowed_origins = allowed_origins
        return self

    def set_are_credentials_allowed(self, are_credentials_allowed: bool) -> HttpServer:
        self.are_credentials_allowed = are_credentials_allowed
        return self

    def set_allowed_methods(self, allowed_methods: list[str]) -> HttpServer:
        self.allowed_methods = allowed_methods
        return self

    def set_allowed_headers(self, allowed_headers: list[str]) -> HttpServer:
        self.allowed_headers = allowed_headers
        return self

    def set_allowed_hosts(self, allowed_hosts: list[str]) -> HttpServer:
        self.allowed_hosts = allowed_hosts
        return self

    def set_allowed_forwarded_hosts(
        self, allowed_forwarded_hosts: list[str]
    ) -> HttpServer:
        self.allowed_forwarded_hosts = allowed_forwarded_hosts
        return self

    async def listen(self) -> None:
        self.add_middleware(
            CORSMiddleware,
            allow_origins=self.allowed_origins,
            allow_credentials=self.are_credentials_allowed,
            allow_methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
        )
        self.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=self.allowed_hosts,
        )

        self.build_routes()

        config = Config(
            app=self,
            host=self.bound_host,
            port=self.http_port,
            log_level="info",
            forwarded_allow_ips=self.allowed_forwarded_hosts,
        )
        config.load()

        self.server = Server(config=config)
        self.server.lifespan = config.lifespan_class(config)
        await self.server.startup()

    async def stop(self) -> None:
        await self.server.shutdown()

    def build_routes(self) -> None: ...
