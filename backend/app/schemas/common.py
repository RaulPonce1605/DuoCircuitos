from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AfterValidator, BaseModel, Field, StringConstraints

DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


def _valid_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("zona horaria IANA inválida") from exc
    return value


Timezone = Annotated[str, Field(max_length=64), AfterValidator(_valid_timezone)]


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
