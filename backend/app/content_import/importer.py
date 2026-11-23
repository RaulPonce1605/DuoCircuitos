"""Carga el temario (`contenido/`) en la base de datos (CLAUDE.md 5.3).

Uso (desde `backend/`): `uv run python -m app.content_import [RUTA]`

- Primero valida todo el temario; si hay un solo error, no escribe nada.
- Es idempotente: actualiza por `slug`, así que correrlo dos veces no cambia nada.
- Lo que desaparece del temario se marca `archived` (no se borra) para no romper el progreso ni
  los intentos que ya lo referencian. Si vuelve a aparecer, se desarchiva con el mismo id.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content_import.schema import LearningPath
from app.content_import.schema import Lesson as LessonFile
from app.content_import.validate import validate_syllabus
from app.models import Exercise, Lesson, Node, Section, Stage, Unit

NODE_TYPE_BY_SYLLABUS = {
    "leccion": "lesson",
    "repaso": "review",
    "cofre": "chest",
    "evaluacion": "assessment",
}

_Row = TypeVar("_Row", Stage, Section, Unit, Lesson, Node, Exercise)


class SyllabusInvalidError(Exception):
    def __init__(self, errors: Sequence[str]) -> None:
        super().__init__(f"el temario tiene {len(errors)} error(es)")
        self.errors = list(errors)


@dataclass
class ImportSummary:
    created: dict[str, int] = field(default_factory=dict)
    updated: dict[str, int] = field(default_factory=dict)
    archived: dict[str, int] = field(default_factory=dict)

    def count(self, bucket: dict[str, int], table: str) -> None:
        bucket[table] = bucket.get(table, 0) + 1

    @property
    def changed(self) -> bool:
        return bool(self.created or self.updated or self.archived)


async def import_syllabus(db: AsyncSession, root: Path) -> ImportSummary:
    report = validate_syllabus(root)
    if not report.ok or report.path is None:
        raise SyllabusInvalidError(report.errors)
    importer = _Importer(db)
    await importer.run(report.path, report.lessons)
    await db.commit()
    return importer.summary


class _Importer:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.summary = ImportSummary()

    async def run(self, path: LearningPath, lessons: dict[str, LessonFile]) -> None:
        stages = await self._existing(Stage)
        sections = await self._existing(Section)
        units = await self._existing(Unit)
        lesson_rows = await self._existing(Lesson)
        nodes = await self._existing(Node)
        seen: dict[type[Any], set[str]] = {model: set() for model in (Stage, Section, Unit, Lesson)}
        seen_nodes: set[str] = set()

        for stage_pos, stage_file in enumerate(path.stages):
            stage = await self._upsert(
                stages, stage_file.id, Stage, title=stage_file.title, position=stage_pos
            )
            seen[Stage].add(stage_file.id)
            for section_pos, section_file in enumerate(stage_file.sections):
                section = await self._upsert(
                    sections,
                    section_file.id,
                    Section,
                    stage_id=stage.id,
                    title=section_file.title,
                    position=section_pos,
                )
                seen[Section].add(section_file.id)
                for unit_pos, unit_file in enumerate(section_file.units):
                    unit = await self._upsert(
                        units,
                        unit_file.id,
                        Unit,
                        section_id=section.id,
                        title=unit_file.title,
                        position=unit_pos,
                    )
                    seen[Unit].add(unit_file.id)
                    ordinal: dict[str, int] = {}
                    for node_pos, node_file in enumerate(unit_file.nodes):
                        node_type = NODE_TYPE_BY_SYLLABUS[node_file.type]
                        lesson_id: int | None = None
                        if node_file.lesson is not None:
                            lesson = await self._import_lesson(
                                lesson_rows, lessons[node_file.lesson], unit.id
                            )
                            seen[Lesson].add(node_file.lesson)
                            lesson_id = lesson.id
                            key = node_file.lesson
                        else:
                            ordinal[node_type] = ordinal.get(node_type, 0) + 1
                            key = f"{unit_file.id}:{node_type}:{ordinal[node_type]}"
                        await self._upsert(
                            nodes,
                            key,
                            Node,
                            key_field="key",
                            unit_id=unit.id,
                            type=node_type,
                            position=node_pos,
                            lesson_id=lesson_id,
                        )
                        seen_nodes.add(key)

        self._archive_missing(stages, seen[Stage])
        self._archive_missing(sections, seen[Section])
        self._archive_missing(units, seen[Unit])
        self._archive_missing(lesson_rows, seen[Lesson])
        self._archive_missing(nodes, seen_nodes)
        await self.db.flush()

    async def _import_lesson(
        self, lesson_rows: dict[str, Lesson], lesson_file: LessonFile, unit_id: int
    ) -> Lesson:
        front = lesson_file.frontmatter
        lesson = await self._upsert(
            lesson_rows,
            front.id,
            Lesson,
            unit_id=unit_id,
            title=front.title,
            objectives=list(front.objectives),
            concepts=list(front.concepts),
            theory=lesson_file.theory,
        )
        existing = {
            row.slug: row
            for row in await self.db.scalars(
                select(Exercise).where(Exercise.lesson_id == lesson.id)
            )
        }
        seen: set[str] = set()
        for position, exercise in enumerate(front.exercises):
            await self._upsert(
                existing,
                exercise.id,
                Exercise,
                lesson_id=lesson.id,
                type=exercise.type,
                position=position,
                prompt=exercise.prompt,
                explanation=exercise.explanation,
                hints=list(exercise.hints),
                # El ejercicio completo, con las claves del temario: los validadores lo leen con
                # los mismos modelos de `schema.py`. Incluye la solución: nunca sale al cliente.
                spec=exercise.model_dump(mode="json", by_alias=True),
            )
            seen.add(exercise.id)
        self._archive_missing(existing, seen)
        return lesson

    async def _existing(self, model: type[_Row]) -> dict[str, _Row]:
        key_field = "key" if model is Node else "slug"
        rows = await self.db.scalars(select(model))
        return {getattr(row, key_field): row for row in rows}

    async def _upsert(
        self,
        rows: dict[str, _Row],
        key: str,
        model: type[_Row],
        *,
        key_field: str = "slug",
        **values: Any,
    ) -> _Row:
        table = model.__tablename__
        row = rows.get(key)
        if row is None:
            row = model(**{key_field: key}, **values)
            self.db.add(row)
            rows[key] = row
            self.summary.count(self.summary.created, table)
        else:
            values["archived"] = False
            changed = {name: v for name, v in values.items() if getattr(row, name) != v}
            for name, value in changed.items():
                setattr(row, name, value)
            if changed:
                self.summary.count(self.summary.updated, table)
        await self.db.flush()
        return row

    def _archive_missing(self, rows: dict[str, _Row], seen: set[str]) -> None:
        for key, row in rows.items():
            if key not in seen and not row.archived:
                row.archived = True
                self.summary.count(self.summary.archived, row.__tablename__)
