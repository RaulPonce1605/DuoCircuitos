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


class AlreadyAnswered(DomainError):
    code = "already_answered"


class NotCurrentExercise(DomainError):
    """Se intentó responder un ejercicio que no es el siguiente de la cola."""

    code = "not_current_exercise"


class AttemptNotCompleted(DomainError):
    code = "attempt_not_completed"


class InvalidAnswer(DomainError):
    """La respuesta no corresponde al tipo del ejercicio o está fuera de rango."""

    code = "invalid_answer"


class UnknownExerciseType(DomainError):
    """Hay un ejercicio en la base cuyo tipo no tiene validador (error de despliegue)."""

    code = "unknown_exercise_type"


class TutorRateLimited(DomainError):
    """El alumno ya usó todas las peticiones al tutor de la última hora."""

    code = "tutor_rate_limited"


class TutorExerciseLimit(DomainError):
    """El alumno ya pidió ayuda el máximo de veces para este ejercicio."""

    code = "tutor_exercise_limit"


class NotEnoughEnergy(DomainError):
    """El alumno se quedó sin energía: debe esperar a que se recargue."""

    code = "not_enough_energy"


class NodeNotPlayable(DomainError):
    """El nodo no tiene ejercicios (un cofre se abre, no se juega)."""

    code = "node_not_playable"


class NotAChest(DomainError):
    """Se intentó abrir como cofre un nodo que no es cofre."""

    code = "not_a_chest"
