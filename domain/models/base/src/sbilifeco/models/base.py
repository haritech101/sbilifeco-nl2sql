from __future__ import annotations
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Response[T](BaseModel):
    is_success: bool = True
    code: int = 200
    message: str = "OK"
    payload: T | None = None

    @classmethod
    def ok(cls, payload: T | None = None) -> Response[T]:
        return cls(payload=payload)

    @classmethod
    def fail(cls, message: str, code: int = 500) -> Response[T]:
        return cls(is_success=False, code=code, message=message, payload=None)

    @classmethod
    def error(cls, e: BaseException) -> Response[T]:
        return cls.fail(message=str(e), code=500)
