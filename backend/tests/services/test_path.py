from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Node, NodeProgress, User
from app.schemas.path import NodeRead, PathRead
from app.services import auth as auth_service
from app.services import path as path_service
from app.services.errors import NodeLocked, NotFound

pytestmark = pytest.mark.usefixtures("syllabus")


def _nodes(path: PathRead) -> list[NodeRead]:
    return [
        node
        for stage in path.stages
        for section in stage.sections
        for unit in section.units
        for node in unit.nodes
    ]


def _status(path: PathRead) -> dict[str, str]:
    return {node.key: node.status for node in _nodes(path)}


async def _complete(db: AsyncSession, user: User, *keys: str) -> None:
    now = datetime.now(UTC)
    for key in keys:
        node_id = await db.scalar(select(Node.id).where(Node.key == key))
        assert node_id is not None, key
        db.add(
            NodeProgress(
                user_id=user.id, node_id=node_id, first_completed_at=now, last_completed_at=now
            )
        )
    await db.flush()


async def test_new_user_only_has_the_first_lesson(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    path = await path_service.get_path(db, user_session.user)
    nodes = _nodes(path)

    assert len(path.stages) == 2
    assert len(nodes) == 25
    assert nodes[0].key == "ohm-01"
    assert nodes[0].status == "available" and nodes[0].is_current
    assert all(node.status == "locked" for node in nodes[1:])
    assert sum(node.is_current for node in nodes) == 1
    assert nodes[0].lesson is not None and nodes[0].lesson.title


async def test_completing_a_lesson_unlocks_the_next(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    await _complete(db, user_session.user, "ohm-01")
    status = _status(await path_service.get_path(db, user_session.user))

    assert status["ohm-01"] == "completed"
    assert status["ohm-02"] == "available"
    assert status["u01-ley-de-ohm:review:1"] == "locked"
    assert status["sp-01"] == "locked"


async def test_finishing_unit_lessons_opens_extras_and_next_unit(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    await _complete(db, user_session.user, "ohm-01", "ohm-02")
    path = await path_service.get_path(db, user_session.user)
    status = _status(path)

    # El repaso es obligatorio: después de él todo sigue bloqueado.
    assert status["u01-ley-de-ohm:review:1"] == "available"
    assert status["u01-ley-de-ohm:chest:1"] == "locked"
    assert status["u01-ley-de-ohm:assessment:1"] == "locked"
    assert status["sp-01"] == "locked"
    current = [node.key for node in _nodes(path) if node.is_current]
    assert current == ["u01-ley-de-ohm:review:1"]

    await _complete(db, user_session.user, "u01-ley-de-ohm:review:1")
    status = _status(await path_service.get_path(db, user_session.user))
    # El cofre aún no frena el avance; la evaluación sí.
    assert status["u01-ley-de-ohm:chest:1"] == "available"
    assert status["u01-ley-de-ohm:assessment:1"] == "available"
    assert status["sp-01"] == "locked"

    await _complete(db, user_session.user, "u01-ley-de-ohm:assessment:1")
    status = _status(await path_service.get_path(db, user_session.user))
    assert status["sp-01"] == "available"
    assert status["sp-02"] == "locked"


async def test_progress_is_per_user(db: AsyncSession, user_session: auth_service.Session) -> None:
    other = await auth_service.register(
        db,
        email="otro@example.com",
        password="contraseña-segura",
        display_name="Otro",
        timezone="UTC",
    )
    await _complete(db, user_session.user, "ohm-01")

    assert _status(await path_service.get_path(db, other.user))["ohm-02"] == "locked"


async def test_archived_nodes_are_hidden(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    chest = await db.scalar(select(Node).where(Node.key == "u01-ley-de-ohm:chest:1"))
    assert chest is not None
    chest.archived = True
    await db.flush()

    assert "u01-ley-de-ohm:chest:1" not in _status(
        await path_service.get_path(db, user_session.user)
    )


async def test_get_unlocked_node(db: AsyncSession, user_session: auth_service.Session) -> None:
    user = user_session.user
    assert (await path_service.get_unlocked_node(db, user, "ohm-01")).key == "ohm-01"
    with pytest.raises(NodeLocked):
        await path_service.get_unlocked_node(db, user, "ohm-02")
    with pytest.raises(NodeLocked):
        await path_service.get_unlocked_node(db, user, "u01-ley-de-ohm:review:1")
    with pytest.raises(NotFound):
        await path_service.get_unlocked_node(db, user, "no-existe")

    await _complete(db, user, "ohm-01", "ohm-02")
    review = await path_service.get_unlocked_node(db, user, "u01-ley-de-ohm:review:1")
    assert (review.type, review.lesson) == ("review", None)
    # Un nodo completado se puede repetir.
    assert (await path_service.get_unlocked_node(db, user, "ohm-01")).key == "ohm-01"
