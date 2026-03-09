from __future__ import annotations
from typing import TypeVar
from traceback import format_exception
from pydantic import BaseModel, ConfigDict
from os.path import basename

T = TypeVar("T")


class Response[T](BaseModel):
    is_success: bool = True
    code: int = 200
    message: str = "OK"
    payload: T | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def ok(cls, payload: T | None = None) -> Response[T]:
        return cls(payload=payload)

    @classmethod
    def fail(cls, message: str, code: int = 500) -> Response[T]:
        return cls(is_success=False, code=code, message=message, payload=None)

    @classmethod
    def error(cls, e: BaseException) -> Response[T]:
        return cls.fail(
            message=f"{e}\n{'\n'.join(format_exception(type(e), value=e, tb=e.__traceback__))}",
            code=500,
        )
