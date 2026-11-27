import shutil
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content_import.importer import SyllabusInvalidError, import_syllabus
from app.content_import.schema import NumericExercise
from app.content_import.validate import DEFAULT_SYLLABUS_DIR
from app.models import Exercise, Lesson, Node, Section, Stage, Unit


@pytest.fixture
def syllabus_copy(tmp_path: Path) -> Path:
    """Copia del temario real para poder modificarla en la prueba."""
    target = tmp_path / "contenido"
    shutil.copytree(DEFAULT_SYLLABUS_DIR, target)
    return target


async def _count(db: AsyncSession, model: type[object], *, archived: bool = False) -> int:
    column = model.archived  # type: ignore[attr-defined]
    total = await db.scalar(select(func.count()).select_from(model).where(column.is_(archived)))
    return int(total or 0)


def _edit(root: Path, relative: str, old: str, new: str) -> None:
    target = root / relative
    text = target.read_text(encoding="utf-8")
    assert old in text
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


async def test_imports_real_syllabus(db: AsyncSession) -> None:
    summary = await import_syllabus(db, DEFAULT_SYLLABUS_DIR)

    assert await _count(db, Stage) == 2
    assert await _count(db, Section) == 4
    assert await _count(db, Unit) == 5
    assert await _count(db, Lesson) == 10
    assert await _count(db, Node) == 25
    assert await _count(db, Exercise) == 55
    assert summary.created["exercises"] == 55
    assert not summary.updated and not summary.archived


async def test_node_keys_order_and_types(db: AsyncSession) -> None:
    await import_syllabus(db, DEFAULT_SYLLABUS_DIR)
    unit = await db.scalar(select(Unit).where(Unit.slug == "u01-ley-de-ohm"))
    assert unit is not None

    nodes = (
        await db.scalars(select(Node).where(Node.unit_id == unit.id).order_by(Node.position))
    ).all()
    assert [(n.key, n.type) for n in nodes] == [
        ("ohm-01", "lesson"),
        ("ohm-02", "lesson"),
        ("u01-ley-de-ohm:review:1", "review"),
        ("u01-ley-de-ohm:chest:1", "chest"),
        ("u01-ley-de-ohm:assessment:1", "assessment"),
    ]
    assert nodes[0].lesson_id is not None and nodes[2].lesson_id is None


async def test_exercise_spec_round_trips_to_the_syllabus_model(db: AsyncSession) -> None:
    await import_syllabus(db, DEFAULT_SYLLABUS_DIR)
    exercise = await db.scalar(select(Exercise).where(Exercise.slug == "ohm-02-corriente"))
    assert exercise is not None

    parsed = NumericExercise.model_validate(exercise.spec)
    assert parsed.solution == "V / R"
    assert parsed.unit == "A"
    assert exercise.type == "numeric"
    assert len(exercise.hints) >= 2


async def test_reimport_is_idempotent(db: AsyncSession) -> None:
    await import_syllabus(db, DEFAULT_SYLLABUS_DIR)
    ids_before = set(await db.scalars(select(Exercise.id)))

    summary = await import_syllabus(db, DEFAULT_SYLLABUS_DIR)

    assert not summary.changed
    assert set(await db.scalars(select(Exercise.id))) == ids_before


async def test_changes_update_rows_in_place(db: AsyncSession, syllabus_copy: Path) -> None:
    await import_syllabus(db, syllabus_copy)
    lesson_id = await db.scalar(select(Lesson.id).where(Lesson.slug == "ohm-01"))
    _edit(
        syllabus_copy,
        "unidades/u01-ley-de-ohm/ohm-01.md",
        "titulo: Voltaje, corriente y resistencia",
        "titulo: Magnitudes básicas",
    )

    summary = await import_syllabus(db, syllabus_copy)

    lesson = await db.scalar(select(Lesson).where(Lesson.slug == "ohm-01"))
    assert lesson is not None
    assert lesson.title == "Magnitudes básicas"
    assert lesson.id == lesson_id
    assert summary.updated == {"lessons": 1}


async def test_removed_content_is_archived_and_restored(
    db: AsyncSession, syllabus_copy: Path
) -> None:
    await import_syllabus(db, syllabus_copy)
    _edit(syllabus_copy, "camino.yaml", "              - { tipo: cofre }\n", "")

    summary = await import_syllabus(db, syllabus_copy)

    assert summary.archived == {"nodes": 1}
    assert await _count(db, Node, archived=True) == 1
    chest = await db.scalar(select(Node).where(Node.key == "u01-ley-de-ohm:chest:1"))
    assert chest is not None and chest.archived

    restored = await import_syllabus(db, DEFAULT_SYLLABUS_DIR)
    assert restored.updated.get("nodes", 0) >= 1
    assert await _count(db, Node, archived=True) == 0


async def test_invalid_syllabus_writes_nothing(db: AsyncSession, syllabus_copy: Path) -> None:
    _edit(syllabus_copy, "unidades/u01-ley-de-ohm/ohm-01.md", "correcta: 2", "correcta: 9")

    with pytest.raises(SyllabusInvalidError) as exc_info:
        await import_syllabus(db, syllabus_copy)

    assert any("correcta" in error for error in exc_info.value.errors)
    assert await _count(db, Lesson) == 0
