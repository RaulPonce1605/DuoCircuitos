import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LessonAttempt, Node, User
from app.models.gamification import XpEvent
from app.services import auth as auth_service
from app.services.gamification import (
    accuracy_percent,
    award_lesson_completion,
    effective_streak,
    lesson_xp,
    local_date,
    register_lesson_day,
)
from app.services.users import user_read

# --- EXP y precisión (cifras por defecto: 10 / 5 / +5) ---------------------------------------


@pytest.mark.parametrize(
    ("count", "first_try", "expected"),
    [
        (5, 5, 55),  # perfecta: 5 · 10 + 5
        (5, 4, 45),  # 4 · 10 + 1 · 5 (ejemplo del documento de diseño)
        (5, 0, 25),
        (1, 1, 15),
        (0, 0, 0),
    ],
)
def test_lesson_xp(count: int, first_try: int, expected: int) -> None:
    assert lesson_xp(count, first_try) == expected


def test_lesson_xp_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError):
        lesson_xp(3, 4)


@pytest.mark.parametrize(
    ("first_try", "count", "expected"),
    [(5, 5, 100), (4, 5, 80), (2, 3, 67), (1, 3, 33), (1, 8, 13), (0, 5, 0), (0, 0, 0)],
)
def test_accuracy_percent(first_try: int, count: int, expected: int) -> None:
    assert accuracy_percent(first_try, count) == expected


# --- Racha -----------------------------------------------------------------------------------


def _user(timezone: str = "America/Mexico_City", **fields: object) -> User:
    user = User(
        id=uuid.uuid4(),
        email="x@example.com",
        display_name="X",
        password_hash="x",
        timezone=timezone,
        xp_total=0,
        streak_current=0,
        streak_longest=0,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        energy_used=0,
        notify_streak_reminder=True,
        notify_challenges=True,
        profile_public=True,
    )
    for name, value in fields.items():
        setattr(user, name, value)
    return user


def test_local_date_uses_the_user_timezone() -> None:
    # 2 de marzo 03:00 UTC = 1 de marzo 21:00 en la Ciudad de México (UTC-6).
    moment = datetime(2026, 3, 2, 3, 0, tzinfo=UTC)
    assert local_date(moment, "America/Mexico_City") == date(2026, 3, 1)
    assert local_date(moment, "UTC") == date(2026, 3, 2)
    assert local_date(moment, "Zona/Inventada") == date(2026, 3, 2)


def test_first_lesson_starts_streak() -> None:
    user = _user()
    assert register_lesson_day(user, datetime(2026, 3, 1, 18, tzinfo=UTC))
    assert (user.streak_current, user.streak_longest) == (1, 1)
    assert user.streak_last_date == date(2026, 3, 1)


def test_second_lesson_same_day_does_not_count_twice() -> None:
    user = _user(streak_current=1, streak_longest=1, streak_last_date=date(2026, 3, 1))
    assert not register_lesson_day(user, datetime(2026, 3, 1, 23, tzinfo=UTC))
    assert user.streak_current == 1


def test_consecutive_day_extends_streak() -> None:
    user = _user(streak_current=4, streak_longest=4, streak_last_date=date(2026, 3, 1))
    assert register_lesson_day(user, datetime(2026, 3, 2, 18, tzinfo=UTC))
    assert (user.streak_current, user.streak_longest) == (5, 5)


def test_missed_day_resets_streak_but_keeps_longest() -> None:
    user = _user(streak_current=4, streak_longest=9, streak_last_date=date(2026, 3, 1))
    assert register_lesson_day(user, datetime(2026, 3, 3, 18, tzinfo=UTC))
    assert (user.streak_current, user.streak_longest) == (1, 9)


def test_streak_day_follows_local_midnight_not_utc() -> None:
    # Lección el 1 de marzo a las 21:00 locales (03:00 UTC del día 2): cuenta como día 1.
    user = _user(streak_current=3, streak_longest=3, streak_last_date=date(2026, 2, 28))
    assert register_lesson_day(user, datetime(2026, 3, 2, 3, tzinfo=UTC))
    assert user.streak_last_date == date(2026, 3, 1)
    assert user.streak_current == 4


@pytest.mark.parametrize(
    ("last", "expected"),
    [
        (None, 0),
        (date(2026, 3, 10), 6),  # hoy
        (date(2026, 3, 9), 6),  # ayer: todavía puede salvarla hoy
        (date(2026, 3, 8), 0),  # antier: rota
    ],
)
def test_effective_streak_breaks_on_read(last: date | None, expected: int) -> None:
    user = _user(streak_current=6, streak_longest=6, streak_last_date=last)
    now = datetime(2026, 3, 10, 18, tzinfo=UTC)  # 12:00 en la Ciudad de México
    assert effective_streak(user, now) == expected
    assert user_read(user, now).streak_current == expected


# --- Entrega de recompensas en la base -------------------------------------------------------


async def _attempt(db: AsyncSession, user: User, count: int = 5) -> LessonAttempt:
    from app.content_import.importer import import_syllabus
    from app.content_import.validate import DEFAULT_SYLLABUS_DIR

    await import_syllabus(db, DEFAULT_SYLLABUS_DIR)
    node = await db.scalar(select(Node).where(Node.key == "ohm-01"))
    assert node is not None
    attempt = LessonAttempt(
        user_id=user.id,
        node_id=node.id,
        lesson_id=node.lesson_id,
        started_at=datetime.now(UTC),
        exercise_count=count,
    )
    db.add(attempt)
    await db.flush()
    return attempt


async def test_award_lesson_completion(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    attempt = await _attempt(db, user)
    now = datetime.now(UTC)

    rewards = await award_lesson_completion(db, user, attempt, first_try_correct=4, now=now)

    assert rewards.xp == 45 and rewards.accuracy == 80
    assert rewards.streak == 1 and rewards.streak_extended
    assert user.xp_total == 45
    assert attempt.completed_at == now and attempt.xp_awarded == 45 and attempt.accuracy == 80
    events = (await db.scalars(select(XpEvent).where(XpEvent.user_id == user.id))).all()
    assert [(e.amount, e.source, e.lesson_attempt_id) for e in events] == [
        (45, "lesson", attempt.id)
    ]


async def test_award_twice_for_same_attempt_is_refused(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    attempt = await _attempt(db, user)
    await award_lesson_completion(db, user, attempt, first_try_correct=5, now=datetime.now(UTC))

    with pytest.raises(ValueError):
        await award_lesson_completion(db, user, attempt, first_try_correct=5, now=datetime.now(UTC))
    assert user.xp_total == 55


async def test_second_lesson_same_day_adds_xp_but_not_streak(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    now = datetime.now(UTC)
    first = await award_lesson_completion(db, user, await _attempt(db, user), 5, now)
    template = await _attempt(db, user)
    second_attempt = LessonAttempt(
        user_id=user.id,
        node_id=template.node_id,
        lesson_id=template.lesson_id,
        started_at=now,
        exercise_count=5,
    )
    db.add(second_attempt)
    await db.flush()
    second = await award_lesson_completion(db, user, second_attempt, 5, now + timedelta(minutes=5))

    assert first.streak_extended and not second.streak_extended
    assert second.streak == 1
    assert user.xp_total == 110
