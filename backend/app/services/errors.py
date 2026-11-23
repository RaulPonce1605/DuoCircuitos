"""Excepciones de dominio (backend/CLAUDE.md 3.11).

Los servicios lanzan estas excepciones; `app/api/errors.py` las traduce a HTTP con un `code`
estable que la app traduce con i18n (`errors.<code>`). Aquí no hay nada de HTTP.
"""


class DomainError(Exception):
    code: str = "domain_error"


class EmailTaken(DomainError):
    code = "email_taken"


class InvalidCredentials(DomainError):
    code = "invalid_credentials"


class InvalidToken(DomainError):
    """Access o refresh token ausente, inválido, expirado o revocado."""

    code = "invalid_token"


class NotFound(DomainError):
    code = "not_found"


class NodeLocked(DomainError):
    """El nodo existe pero el usuario aún no lo desbloquea."""

    code = "node_locked"


class InvalidAnswer(DomainError):
    """La respuesta no corresponde al tipo del ejercicio o está fuera de rango."""

    code = "invalid_answer"


class UnknownExerciseType(DomainError):
    """Hay un ejercicio en la base cuyo tipo no tiene validador (error de despliegue)."""

    code = "unknown_exercise_type"
