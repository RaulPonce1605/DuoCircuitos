"""Cofres (docs/diseno/cofres-y-logros.md). El premio lo decide el backend (CLAUDE.md 5.4).

- Al terminar un intento (lección, repaso o evaluación) sale un cofre cerrado; el resumen trae su
  id y la app lo abre en la pantalla "Pulsa para abrir".
- El nodo cofre del camino se abre una sola vez por alumno, da un premio mayor y cuenta como nodo
  completado.
- El premio (EXP y energía) se sortea al abrir y se guarda: abrirlo de nuevo no da más.
"""

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Chest, LessonAttempt, NodeProgress, User, XpEvent
from app.schemas.achievements import BadgeRead, ChestRead, ChestRewardRead
from app.services import achievements, challenges, energy
from app.services import path as path_service
from app.services.errors import NotAChest, NotFound
from app.services.users import energy_read


def create_for_attempt(db: AsyncSession, user: User, attempt: LessonAttempt) -> Chest:
    chest = Chest(id=uuid.uuid4(), user_id=user.id, source="lesson", lesson_attempt_id=attempt.id)
    db.add(chest)
    return chest


async def open_chest(db: AsyncSession, user: User, chest_id: uuid.UUID) -> ChestRead:
    chest = await db.scalar(
        select(Chest).where(Chest.id == chest_id, Chest.user_id == user.id).with_for_update()
    )
    if chest is None:
        raise NotFound
    return await _open(db, user, chest, datetime.now(UTC))


async def open_node_chest(db: AsyncSession, user: User, node_key: str) -> ChestRead:
    node = await path_service.get_unlocked_node(db, user, node_key)
    if node.type != "chest":
        raise NotAChest
    now = datetime.now(UTC)
    await db.refresh(user, with_for_update=True)  # serializa dos aperturas a la vez
    chest = await db.scalar(select(Chest).where(Chest.user_id == user.id, Chest.node_id == node.id))
    if chest is None:
        chest = Chest(id=uuid.uuid4(), user_id=user.id, source="node", node_id=node.id)
        db.add(chest)
        db.add(
            NodeProgress(
                user_id=user.id, node_id=node.id, first_completed_at=now, last_completed_at=now
            )
        )
        await db.flush()
    return await _open(db, user, chest, now)


async def _open(db: AsyncSession, user: User, chest: Chest, now: datetime) -> ChestRead:
    new_badges: list[BadgeRead] = []
    if chest.opened_at is None:
        await db.refresh(user, with_for_update=True)
        settings = get_settings()
        if chest.source == "node":
            xp = _roll(settings.chest_node_xp_min, settings.chest_node_xp_max)
            energy_reward = settings.chest_node_energy
        else:
            xp = _roll(settings.chest_lesson_xp_min, settings.chest_lesson_xp_max)
            energy_reward = settings.chest_lesson_energy
        chest.opened_at = now
        chest.reward_xp = xp
        chest.reward_energy = energy_reward
        user.xp_total += xp
        if xp > 0:
            db.add(XpEvent(user_id=user.id, amount=xp, source="chest"))
        energy.refill(user, energy_reward, now)
        await db.flush()
        await challenges.record(db, user, now, {"earn_xp": xp, "open_chests": 1})
        new_badges = await achievements.evaluate(db, user, now)
    read = _chest_read(chest, user, now, new_badges)
    await db.commit()
    return read


def _roll(low: int, high: int) -> int:
    return low + secrets.randbelow(high - low + 1)


def _chest_read(chest: Chest, user: User, now: datetime, new_badges: list[BadgeRead]) -> ChestRead:
    reward = (
        ChestRewardRead(xp=chest.reward_xp or 0, energy=chest.reward_energy or 0)
        if chest.opened_at is not None
        else None
    )
    return ChestRead(
        id=chest.id,
        source="node" if chest.source == "node" else "lesson",
        reward=reward,
        new_badges=new_badges,
        energy=energy_read(user, now),
    )
