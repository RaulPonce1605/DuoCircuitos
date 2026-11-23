from typing import Literal

from pydantic import BaseModel


class ErrorRead(BaseModel):
    """Error con un código estable que la app traduce (`errors.<code>`)."""

    code: str


class ValidationIssue(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorRead(BaseModel):
    """422: el cuerpo o los parámetros no pasan la validación."""

    code: Literal["validation_error"]
    detail: list[ValidationIssue]


class StatusRead(BaseModel):
    status: Literal["ok"]
