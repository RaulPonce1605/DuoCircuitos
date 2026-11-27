import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Exercise,
    ExerciseInstance,
    Lesson,
    LessonAttempt,
    Node,
    NodeProgress,
    Section,
    Stage,
    Unit,
    User,
)


async def _make_user(db: AsyncSession, email: str = "ana@example.com") -> User:
    user = User(email=email, display_name="Ana", password_hash="x")
    db.add(user)
    await db.flush()
    return user


async def _make_unit(db: AsyncSession) -> Unit:
    stage = Stage(slug="e1", title="Etapa", position=0)
    section = Section(slug="s1", title="Sección", position=0, stage=stage)
    unit = Unit(slug="u1", title="Unidad", position=0, section=section)
    db.add(unit)
    await db.flush()
    return unit


async def _make_lesson(db: AsyncSession, unit: Unit) -> Lesson:
    lesson = Lesson(
        unit_id=unit.id, slug="l1", title="Lección", objectives=["o"], concepts=["c"], theory="t"
    )
    db.add(lesson)
    await db.flush()
    return lesson


async def test_user_defaults(db: AsyncSession) -> None:
    user = await _make_user(db)
    await db.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert (user.xp_total, user.streak_current, user.streak_longest) == (0, 0, 0)
    assert user.timezone == "UTC"
    assert user.streak_last_date is None
    assert user.created_at is not None


async def test_email_is_unique(db: AsyncSession) -> None:
    await _make_user(db)
    with pytest.raises(IntegrityError):
        await _make_user(db)


async def test_streak_longest_cannot_be_below_current(db: AsyncSession) -> None:
    user = await _make_user(db)
    user.streak_current = 3
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_lesson_node_requires_lesson(db: AsyncSession) -> None:
    unit = await _make_unit(db)
    db.add(Node(unit_id=unit.id, key="u1:lesson:1", type="lesson", position=0))
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_node_type_is_checked(db: AsyncSession) -> None:
    unit = await _make_unit(db)
    db.add(Node(unit_id=unit.id, key="u1:otro:1", type="otro", position=0))
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_full_attempt_graph(db: AsyncSession) -> None:
    user = await _make_user(db)
    unit = await _make_unit(db)
    lesson = await _make_lesson(db, unit)
    node = Node(unit_id=unit.id, key="l1", type="lesson", position=0, lesson_id=lesson.id)
    exercise = Exercise(
        lesson_id=lesson.id,
        slug="ex1",
        type="numeric",
        position=0,
        prompt="p",
        explanation="e",
        hints=["a", "b"],
        spec={"solucion": "V / R"},
    )
    db.add_all([node, exercise])
    await db.flush()

    now = datetime.now(UTC)
    attempt = LessonAttempt(
        user_id=user.id, node_id=node.id, lesson_id=lesson.id, started_at=now, exercise_count=1
    )
    db.add(attempt)
    await db.flush()
    db.add(
        ExerciseInstance(
            attempt_id=attempt.id, exercise_id=exercise.id, position=0, seed=42, state={"V": 5}
        )
    )
    db.add(
        NodeProgress(
            user_id=user.id, node_id=node.id, first_completed_at=now, last_completed_at=now
        )
    )
    await db.flush()

    instance = await db.scalar(select(ExerciseInstance).where(ExerciseInstance.seed == 42))
    assert instance is not None
    assert instance.state == {"V": 5}
    assert instance.is_retry is False


async def test_xp_only_set_when_attempt_completed(db: AsyncSession) -> None:
    user = await _make_user(db)
    unit = await _make_unit(db)
    lesson = await _make_lesson(db, unit)
    node = Node(unit_id=unit.id, key="n-xp", type="lesson", position=0, lesson_id=lesson.id)
    db.add(node)
    await db.flush()
    db.add(
        LessonAttempt(
            user_id=user.id,
            node_id=node.id,
            lesson_id=lesson.id,
            started_at=datetime.now(UTC),
            exercise_count=1,
            xp_awarded=10,
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
