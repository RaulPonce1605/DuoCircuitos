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
    """422. `validation_error`: el cuerpo o los parámetros no pasan la validación (trae
    `detail`). Otros códigos (`invalid_answer`) son errores de dominio sin `detail`."""

    code: str
    detail: list[ValidationIssue] = []


class StatusRead(BaseModel):
    status: Literal["ok"]
