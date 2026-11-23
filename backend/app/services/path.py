"""El camino de aprendizaje y qué nodos tiene desbloqueados cada usuario (CLAUDE.md 1.1).

Regla: un nodo se desbloquea cuando están completos todos los nodos **obligatorios** anteriores
en el orden global del camino (etapa → sección → unidad → nodo).

En la fase 1 solo las lecciones son obligatorias. Repaso, cofre y evaluación se muestran y se
desbloquean con la misma regla, pero no frenan el avance porque aún no se pueden jugar
(fase 2). Cuando existan, se agregan a `REQUIRED_NODE_TYPES`.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Lesson, Node, NodeProgress, Section, Stage, Unit, User
from app.schemas.path import (
    LessonSummaryRead,
    NodeRead,
    NodeStatus,
    PathRead,
    SectionRead,
    StageRead,
    UnitRead,
)
from app.services.errors import NodeLocked, NotFound

REQUIRED_NODE_TYPES = frozenset({"lesson"})


@dataclass(frozen=True)
class _PlacedNode:
    node: Node
    status: NodeStatus


async def get_path(db: AsyncSession, user: User) -> PathRead:
    stages = await _load_stages(db)
    statuses = _compute_statuses(_ordered_nodes(stages), await _completed_node_ids(db, user.id))
    current = next(
        (
            node_id
            for node_id, placed in statuses.items()
            if placed.status == "available" and placed.node.type == "lesson"
        ),
        None,
    )
    return PathRead(
        stages=[
            StageRead(
                slug=stage.slug,
                title=stage.title,
                sections=[
                    SectionRead(
                        slug=section.slug,
                        title=section.title,
                        units=[
                            UnitRead(
                                slug=unit.slug,
                                title=unit.title,
                                nodes=[
                                    _node_read(statuses[node.id], node.id == current)
                                    for node in _active(unit.nodes)
                                ],
                            )
                            for unit in _active(section.units)
                        ],
                    )
                    for section in _active(stage.sections)
                ],
            )
            for stage in stages
        ]
    )


async def get_unlocked_lesson(db: AsyncSession, user: User, lesson_slug: str) -> Lesson:
    """La lección, si existe y el usuario la tiene desbloqueada. Si no: NotFound o NodeLocked."""
    node = await db.scalar(
        select(Node)
        .join(Lesson, Node.lesson_id == Lesson.id)
        .where(Lesson.slug == lesson_slug, Node.archived.is_(False), Lesson.archived.is_(False))
        .options(selectinload(Node.lesson))
    )
    if node is None or node.lesson is None:
        raise NotFound
    stages = await _load_stages(db)
    statuses = _compute_statuses(_ordered_nodes(stages), await _completed_node_ids(db, user.id))
    placed = statuses.get(node.id)
    if placed is None or placed.status == "locked":
        raise NodeLocked
    return node.lesson


async def _load_stages(db: AsyncSession) -> list[Stage]:
    result = await db.scalars(
        select(Stage)
        .where(Stage.archived.is_(False))
        .order_by(Stage.position)
        .options(
            selectinload(Stage.sections)
            .selectinload(Section.units)
            .selectinload(Unit.nodes)
            .selectinload(Node.lesson)
        )
    )
    return list(result)


def _active[T: (Section, Unit, Node)](rows: list[T]) -> list[T]:
    return sorted((row for row in rows if not row.archived), key=lambda row: row.position)


def _ordered_nodes(stages: list[Stage]) -> list[Node]:
    return [
        node
        for stage in stages
        for section in _active(stage.sections)
        for unit in _active(section.units)
        for node in _active(unit.nodes)
    ]


async def _completed_node_ids(db: AsyncSession, user_id: uuid.UUID) -> set[int]:
    return set(
        await db.scalars(select(NodeProgress.node_id).where(NodeProgress.user_id == user_id))
    )


def _compute_statuses(nodes: list[Node], completed: set[int]) -> dict[int, _PlacedNode]:
    statuses: dict[int, _PlacedNode] = {}
    blocked = False  # ¿hay algún nodo obligatorio anterior sin completar?
    for node in nodes:
        if node.id in completed:
            status: NodeStatus = "completed"
        elif blocked:
            status = "locked"
        else:
            status = "available"
        statuses[node.id] = _PlacedNode(node, status)
        if node.type in REQUIRED_NODE_TYPES and status != "completed":
            blocked = True
    return statuses


def _node_read(placed: _PlacedNode, is_current: bool) -> NodeRead:
    node = placed.node
    lesson = (
        LessonSummaryRead(slug=node.lesson.slug, title=node.lesson.title)
        if node.lesson is not None
        else None
    )
    return NodeRead(
        key=node.key,
        type=node.type,  # Pydantic valida el Literal; la base lo garantiza con un CHECK
        status=placed.status,
        is_current=is_current,
        lesson=lesson,
    )
