"""Temario cargado desde `contenido/` por el importador. Nunca se edita a mano (CLAUDE.md 5.3).

Cada fila guarda el `slug` del temario (su id en `contenido/`), que es estable. Lo que se quita del
temario no se borra: se marca `archived` para no romper el progreso ni los intentos ya guardados.
"""

from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

NODE_TYPES = ("lesson", "review", "chest", "assessment")


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    position: Mapped[int]
    archived: Mapped[bool] = mapped_column(default=False, server_default="false")

    sections: Mapped[list["Section"]] = relationship(
        back_populates="stage", order_by="Section.position"
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    position: Mapped[int]
    archived: Mapped[bool] = mapped_column(default=False, server_default="false")

    stage: Mapped[Stage] = relationship(back_populates="sections")
    units: Mapped[list["Unit"]] = relationship(back_populates="section", order_by="Unit.position")


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    position: Mapped[int]
    archived: Mapped[bool] = mapped_column(default=False, server_default="false")

    section: Mapped[Section] = relationship(back_populates="units")
    nodes: Mapped[list["Node"]] = relationship(back_populates="unit", order_by="Node.position")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    objectives: Mapped[list[str]]
    concepts: Mapped[list[str]]
    theory: Mapped[str] = mapped_column(Text)
    archived: Mapped[bool] = mapped_column(default=False, server_default="false")

    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="lesson", order_by="Exercise.position"
    )


class Node(Base):
    """Paso del camino. `key` es estable: slug de la lección, o `unidad:tipo:n` para los demás."""

    __tablename__ = "nodes"
    __table_args__ = (
        CheckConstraint(f"type IN {NODE_TYPES}", name="type_valid"),
        CheckConstraint(
            "(type = 'lesson') = (lesson_id IS NOT NULL)", name="lesson_id_only_on_lessons"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    key: Mapped[str] = mapped_column(String(150), unique=True)
    type: Mapped[str] = mapped_column(String(20))
    position: Mapped[int]
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id"), unique=True)
    archived: Mapped[bool] = mapped_column(default=False, server_default="false")

    unit: Mapped[Unit] = relationship(back_populates="nodes")
    lesson: Mapped[Lesson | None] = relationship()


class Exercise(Base):
    """Ejercicio del temario. `spec` guarda los campos propios del tipo, incluida la solución.

    La solución NUNCA sale al cliente antes de Comprobar: los schemas públicos no la incluyen.
    """

    __tablename__ = "exercises"
    __table_args__ = (UniqueConstraint("lesson_id", "slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    slug: Mapped[str] = mapped_column(String(100))
    # Id del tipo en el registro de validadores (multiple_choice, fill_pattern, numeric...).
    type: Mapped[str] = mapped_column(String(40))
    position: Mapped[int]
    prompt: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    hints: Mapped[list[str]]
    spec: Mapped[dict[str, Any]]
    archived: Mapped[bool] = mapped_column(default=False, server_default="false")

    lesson: Mapped[Lesson] = relationship(back_populates="exercises")
