from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import ChallengeTemplate, get_settings
from app.models import Challenge, XpEvent
from app.services import auth as auth_service
from app.services import challenges

# 18:00 UTC = 12:00 en la Ciudad de México (zona de la alumna de prueba).
NOW = datetime(2026, 11, 26, 18, tzinfo=UTC)


def test_daily_templates_are_stable_per_user_and_day(user_session: auth_service.Session) -> None:
    user = user_session.user
    today = NOW.date()

    first = challenges.daily_templates(user, today)
    again = challenges.daily_templates(user, today)

    assert first == again
    assert len(first) == 3
    assert len({t.kind for t in first}) == 3


async def test_ensure_creates_the_day_and_month_once(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    first = await challenges.ensure(db, user, NOW)
    second = await challenges.ensure(db, user, NOW)

    assert [c.id for c in first] == [c.id for c in second]
    assert sorted(c.period for c in first) == ["daily"] * 3 + ["monthly"]
    monthly = next(c for c in first if c.period == "monthly")
    assert monthly.period_start.isoformat() == "2026-11-01"
    total = await db.scalar(select(func.count()).where(Challenge.user_id == user.id))
    assert total == 4


async def test_a_new_local_day_brings_new_daily_challenges(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    await challenges.ensure(db, user, NOW)
    # 05:59 UTC del día siguiente todavía es el 26 en la Ciudad de México.
    same_day = await challenges.ensure(db, user, NOW + timedelta(hours=11, minutes=59))
    next_day = await challenges.ensure(db, user, NOW + timedelta(days=1))

    assert {c.period_start.isoformat() for c in same_day if c.period == "daily"} == {"2026-11-26"}
    assert {c.period_start.isoformat() for c in next_day if c.period == "daily"} == {"2026-11-27"}
    # El mensual es el mismo.
    assert len({c.id for c in same_day + next_day if c.period == "monthly"}) == 1


async def test_record_completes_and_pays_once(
    db: AsyncSession, user_session: auth_service.Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        get_settings(),
        "daily_challenges",
        [ChallengeTemplate(kind="complete_lessons", goal=2, reward_xp=10)],
    )
    monkeypatch.setattr(
        get_settings(),
        "monthly_challenges",
        [ChallengeTemplate(kind="earn_xp", goal=30, reward_xp=100)],
    )
    user = user_session.user

    first = await challenges.record(db, user, NOW, {"complete_lessons": 1, "earn_xp": 20})
    second = await challenges.record(db, user, NOW, {"complete_lessons": 1, "earn_xp": 5})
    third = await challenges.record(db, user, NOW, {"complete_lessons": 1})

    assert first == []
    assert [c.kind for c in second] == ["complete_lessons"]
    assert third == []
    assert user.xp_total == 10  # la EXP del desafío diario
    rows = {c.kind: c for c in await challenges.ensure(db, user, NOW)}
    assert (rows["complete_lessons"].progress, rows["complete_lessons"].completed_at) == (2, NOW)
    # Los 10 EXP del desafío no cuentan para "gana EXP": van 25 de 30.
    assert rows["earn_xp"].progress == 25
    events = await db.scalar(
        select(func.count()).where(XpEvent.user_id == user.id, XpEvent.source == "challenge")
    )
    assert events == 1


async def test_overview_has_period_ends_at_local_midnight(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    overview = await challenges.overview(db, user_session.user, NOW)

    assert len(overview.daily) == 3
    assert len(overview.monthly) == 1
    # Medianoche del 27 en la Ciudad de México (UTC-6) = 06:00 UTC.
    assert overview.daily_ends_at.astimezone(UTC) == datetime(2026, 11, 27, 6, tzinfo=UTC)
    assert overview.monthly_ends_at.astimezone(UTC) == datetime(2026, 12, 1, 6, tzinfo=UTC)
