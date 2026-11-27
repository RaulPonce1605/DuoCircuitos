"""Traduce las excepciones de dominio a respuestas HTTP con un `code` estable."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorRead, ValidationErrorRead, ValidationIssue
from app.services import errors

# Para los routers con parámetros o cuerpo: documenta el 422 con NUESTRO formato
# (si no, FastAPI documenta el suyo y el cliente generado tendría tipos que no coinciden).
VALIDATION_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    422: {"model": ValidationErrorRead, "description": "validation_error"}
}

STATUS_BY_ERROR: dict[type[errors.DomainError], int] = {
    errors.EmailTaken: 409,
    errors.InvalidCredentials: 401,
    errors.InvalidToken: 401,
    errors.NotFound: 404,
    errors.NodeLocked: 409,
    errors.AlreadyAnswered: 409,
    errors.NotCurrentExercise: 409,
    errors.AttemptNotCompleted: 409,
    errors.InvalidAnswer: 422,
    errors.UnknownExerciseType: 500,
    errors.TutorRateLimited: 429,
    errors.NotEnoughEnergy: 409,
    errors.NodeNotPlayable: 409,
    errors.NotAChest: 409,
    errors.NotEnoughCoins: 409,
    errors.CannotFollowSelf: 409,
    errors.EnergyAlreadyFull: 409,
    errors.StreakFreezeLimit: 409,
    errors.TutorExerciseLimit: 429,
}


def error_responses(*error_types: type[errors.DomainError]) -> dict[int | str, dict[str, Any]]:
    """Documenta en el OpenAPI los errores que puede devolver una ruta."""
    responses: dict[int | str, dict[str, Any]] = {}
    for error_type in error_types:
        status = STATUS_BY_ERROR[error_type]
        # Un 422 de dominio comparte schema con el de validación: un solo tipo por código HTTP.
        model = ValidationErrorRead if status == 422 else ErrorRead
        responses.setdefault(status, {"model": model, "description": "validation_error"})
        if status != 422 and responses[status]["description"] == "validation_error":
            responses[status]["description"] = ""
        codes = responses[status]["description"]
        responses[status]["description"] = (
            f"{codes}, {error_type.code}" if codes else error_type.code
        )
    return responses


def domain_error_response(exc: errors.DomainError) -> JSONResponse:
    status = STATUS_BY_ERROR.get(type(exc), 400)
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return JSONResponse(ErrorRead(code=exc.code).model_dump(), status, headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(errors.DomainError)
    async def _domain_error(_: Request, exc: errors.DomainError) -> JSONResponse:
        return domain_error_response(exc)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Se conserva `detail` (útil para depurar); la app solo mira `code`.
        body = ValidationErrorRead(
            code="validation_error",
            detail=[
                ValidationIssue(loc=list(error["loc"]), msg=error["msg"], type=error["type"])
                for error in exc.errors()
            ],
        )
        return JSONResponse(body.model_dump(), 422)
