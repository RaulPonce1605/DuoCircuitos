"""EXP, precisión y racha (docs/diseno/exp-y-racha.md). El backend es la fuente de verdad.

Las cifras salen de `Settings` (XP_*); aquí no hay números de gamificación fijos.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import LessonAttempt, User
from app.models.gamification import XpEvent


@dataclass(frozen=True)
class LessonRewards:
    xp: int
    accuracy: int
    streak: int
    streak_extended: bool


def lesson_xp(exercise_count: int, first_try_correct: int) -> int:
    """EXP de una lección terminada: cada ejercicio cuenta una vez."""
    if not 0 <= first_try_correct <= exercise_count:
        raise ValueError("first_try_correct fuera de rango")
    settings = get_settings()
    retried = exercise_count - first_try_correct
    xp = (
        first_try_correct * settings.xp_per_exercise_first_try
        + retried * settings.xp_per_exercise_retry
    )
    if exercise_count > 0 and retried == 0:
        xp += settings.xp_perfect_lesson_bonus
    return xp


def accuracy_percent(first_try_correct: int, exercise_count: int) -> int:
    """Porcentaje entero, redondeando 0.5 hacia arriba (2/3 → 67)."""
    if exercise_count <= 0:
        return 0
    return (200 * first_try_correct + exercise_count) // (2 * exercise_count)


def local_date(moment: datetime, timezone: str) -> date:
    """Día calendario del alumno. Una zona inválida cae a UTC (nunca debería pasar: se valida
    al registrarse)."""
    try:
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        zone = ZoneInfo("UTC")
    return moment.astimezone(zone).date()


def effective_streak(user: User, now: datetime) -> int:
    """La racha que se muestra: se rompe sola si el último día con lección es anterior a ayer."""
    if user.streak_last_date is None:
        return 0
    today = local_date(now, user.timezone)
    if user.streak_last_date < today - timedelta(days=1):
        return 0
    return user.streak_current


def register_lesson_day(user: User, now: datetime) -> bool:
    """Actualiza la racha porque terminó una lección. Devuelve True si la racha subió."""
    today = local_date(now, user.timezone)
    last = user.streak_last_date
    if last is not None and last >= today:
        return False  # ya contó hoy (o un cambio de zona horaria lo dejó "en el futuro")
    if last == today - timedelta(days=1):
        user.streak_current += 1
    else:
        user.streak_current = 1
    user.streak_last_date = today
    user.streak_longest = max(user.streak_longest, user.streak_current)
    return True


async def award_lesson_completion(
    db: AsyncSession, user: User, attempt: LessonAttempt, first_try_correct: int, now: datetime
) -> LessonRewards:
    """Marca el intento como terminado y entrega EXP y racha. Una sola vez por intento."""
    if attempt.completed_at is not None:
        raise ValueError("el intento ya estaba completado")
    xp = lesson_xp(attempt.exercise_count, first_try_correct)
    accuracy = accuracy_percent(first_try_correct, attempt.exercise_count)
    extended = register_lesson_day(user, now)

    attempt.completed_at = now
    attempt.first_try_correct = first_try_correct
    attempt.accuracy = accuracy
    attempt.xp_awarded = xp
    attempt.streak_extended = extended
    user.xp_total += xp
    if xp > 0:
        db.add(XpEvent(user_id=user.id, amount=xp, source="lesson", lesson_attempt_id=attempt.id))
    await db.flush()
    return LessonRewards(
        xp=xp, accuracy=accuracy, streak=user.streak_current, streak_extended=extended
    )
