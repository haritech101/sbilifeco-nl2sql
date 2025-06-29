from __future__ import annotations
from pydantic import BaseModel


class KPI(BaseModel):
    id: str = ""
    name: str
    aka: str = ""
    description: str = ""
    formula: str = ""


class Field(BaseModel):
    id: str = ""
    name: str
    type: str = "text"
    description: str = ""
    aka: str = ""


class Table(BaseModel):
    id: str = ""
    name: str
    description: str = ""
    fields: list[Field] | None = None


class DB(BaseModel):
    id: str = ""
    name: str
    description: str = ""
    tables: list[Table] | None = None
    kpis: list[KPI] | None = None
    additional_info: str | None = None
