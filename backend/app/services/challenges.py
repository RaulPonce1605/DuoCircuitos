"""Desafíos diarios y mensual (docs/diseno/desafios.md). El backend es la fuente de verdad.

- Cada día local del alumno se eligen `DAILY_CHALLENGE_COUNT` metas de la lista diaria (siempre
  las mismas para ese alumno y ese día). Cada mes se usan todas las metas de la lista mensual.
- No hay tareas programadas: los desafíos del periodo se crean la primera vez que se leen o que
  el alumno gana EXP.
- Al cumplir una meta se entrega su EXP (evento `source = "challenge"`). Esa EXP no cuenta para
  otros desafíos de "gana EXP", para que un desafío no complete a otro.
"""

import calendar
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from random import Random
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import ChallengeKind, ChallengeTemplate, get_settings
from app.models import Challenge, User, XpEvent
from app.schemas.challenges import ChallengeRead, ChallengesRead
from app.services.gamification import local_date


def _zone(timezone: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")


def daily_templates(user: User, day: date) -> list[ChallengeTemplate]:
    """Las metas del día: al azar, pero siempre las mismas para el mismo alumno y día."""
    settings = get_settings()
    pool = list(settings.daily_challenges)
    rng = Random(f"{user.id}:{day.isoformat()}")  # noqa: S311 - no es criptográfico
    return rng.sample(pool, min(settings.daily_challenge_count, len(pool)))


def _periods(user: User, now: datetime) -> tuple[date, date]:
    today = local_date(now, user.timezone)
    return today, today.replace(day=1)


async def ensure(db: AsyncSession, user: User, now: datetime) -> list[Challenge]:
    """Crea (si faltan) y devuelve los desafíos del día y del mes del alumno."""
    today, month = _periods(user, now)
    rows = [
        {
            "period": "daily",
            "period_start": today,
            "kind": t.kind,
            "goal": t.goal,
            "reward_xp": t.reward_xp,
        }
        for t in daily_templates(user, today)
    ] + [
        {
            "period": "monthly",
            "period_start": month,
            "kind": t.kind,
            "goal": t.goal,
            "reward_xp": t.reward_xp,
        }
        for t in get_settings().monthly_challenges
    ]
    if rows:
        # Dos peticiones a la vez no duplican: la restricción única decide y la otra no hace nada.
        await db.execute(
            insert(Challenge)
            .values([{"user_id": user.id, **row} for row in rows])
            .on_conflict_do_nothing(index_elements=["user_id", "period", "period_start", "kind"])
        )
    result = await db.scalars(
        select(Challenge)
        .where(
            Challenge.user_id == user.id,
            (
                ((Challenge.period == "daily") & (Challenge.period_start == today))
                | ((Challenge.period == "monthly") & (Challenge.period_start == month))
            ),
        )
        .order_by(Challenge.period, Challenge.created_at, Challenge.kind)
        .execution_options(populate_existing=True)
    )
    return list(result)


async def record(
    db: AsyncSession, user: User, now: datetime, progress: Mapping[ChallengeKind, int]
) -> list[Challenge]:
    """Suma avance a los desafíos activos y entrega la EXP de los que se completan.

    La fila del usuario debe estar bloqueada (se le suma EXP). Devuelve los recién completados.
    """
    completed: list[Challenge] = []
    for challenge in await ensure(db, user, now):
        amount = progress.get(challenge.kind, 0)  # type: ignore[call-overload]
        if challenge.completed_at is not None or amount <= 0:
            continue
        challenge.progress = min(challenge.goal, challenge.progress + amount)
        if challenge.progress >= challenge.goal:
            challenge.completed_at = now
            completed.append(challenge)
            if challenge.reward_xp > 0:
                user.xp_total += challenge.reward_xp
                db.add(XpEvent(user_id=user.id, amount=challenge.reward_xp, source="challenge"))
    await db.flush()
    return completed


def _period_end(user: User, start: date, period: str) -> datetime:
    """Cuándo termina el periodo, en la medianoche local del alumno."""
    if period == "daily":
        end = start + timedelta(days=1)
    else:
        days = calendar.monthrange(start.year, start.month)[1]
        end = start + timedelta(days=days)
    return datetime.combine(end, time.min, tzinfo=_zone(user.timezone))


def challenge_read(challenge: Challenge) -> ChallengeRead:
    return ChallengeRead.model_validate(challenge)


async def overview(db: AsyncSession, user: User, now: datetime) -> ChallengesRead:
    challenges = await ensure(db, user, now)
    await db.commit()
    today, month = _periods(user, now)
    return ChallengesRead(
        daily=[challenge_read(c) for c in challenges if c.period == "daily"],
        monthly=[challenge_read(c) for c in challenges if c.period == "monthly"],
        daily_ends_at=_period_end(user, today, "daily"),
        monthly_ends_at=_period_end(user, month, "monthly"),
    )
