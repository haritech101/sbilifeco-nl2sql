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
        description = e.__class__.__name__ + "\n"
        description += "\n".join(e.args) if e.args else ""
        description += "\n".join(e.__notes__) if hasattr(e, "__notes__") else ""
        tb = e.__traceback__
        if tb:
            description += f"\n{tb.tb_frame.f_code.co_filename}:{tb.tb_lineno}"
        return cls.fail(message=description, code=500)
