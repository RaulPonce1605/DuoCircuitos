"""Logros y medallas (docs/diseno/cofres-y-logros.md).

Un logro tiene niveles (umbrales de una métrica). Cada nivel alcanzado entrega una medalla, que se
guarda una sola vez. Los logros y sus umbrales viven en `Settings.achievements`; los nombres, en
la app (i18n).
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import AchievementDefinition, AchievementMetric, get_settings
from app.models import Badge, Chest, LessonAttempt, Node, NodeProgress, User
from app.schemas.achievements import AchievementRead, AchievementsRead, BadgeRead


async def metrics(db: AsyncSession, user: User) -> dict[AchievementMetric, int]:
    """El valor actual de cada métrica de logros para el usuario."""

    async def completed_nodes(node_type: str) -> int:
        count = await db.scalar(
            select(func.count())
            .select_from(NodeProgress)
            .join(Node, NodeProgress.node_id == Node.id)
            .where(NodeProgress.user_id == user.id, Node.type == node_type)
        )
        return int(count or 0)

    perfect = await db.scalar(
        select(func.count())
        .select_from(LessonAttempt)
        .join(Node, LessonAttempt.node_id == Node.id)
        .where(
            LessonAttempt.user_id == user.id,
            LessonAttempt.accuracy == 100,
            Node.type == "lesson",
        )
    )
    chests = await db.scalar(
        select(func.count()).where(Chest.user_id == user.id, Chest.opened_at.is_not(None))
    )
    return {
        "lessons_completed": await completed_nodes("lesson"),
        "streak_longest": user.streak_longest,
        "xp_total": user.xp_total,
        "perfect_lessons": int(perfect or 0),
        "units_completed": await completed_nodes("assessment"),
        "chests_opened": int(chests or 0),
    }


def _definitions() -> dict[str, AchievementDefinition]:
    return {definition.id: definition for definition in get_settings().achievements}


def badge_read(badge: Badge) -> BadgeRead | None:
    definition = _definitions().get(badge.achievement_id)
    if definition is None or badge.level > len(definition.thresholds):
        return None  # el logro se quitó de la configuración: la medalla no se muestra
    return BadgeRead(
        achievement_id=badge.achievement_id,
        level=badge.level,
        threshold=definition.thresholds[badge.level - 1],
        earned_at=badge.earned_at,
    )


async def evaluate(
    db: AsyncSession, user: User, now: datetime, *, attempt_id: uuid.UUID | None = None
) -> list[BadgeRead]:
    """Entrega las medallas recién alcanzadas y las devuelve. Llamar después de cualquier cambio
    que mueva una métrica (terminar un intento, abrir un cofre...)."""
    values = await metrics(db, user)
    owned = {
        (row.achievement_id, row.level)
        for row in await db.scalars(select(Badge).where(Badge.user_id == user.id))
    }
    new: list[Badge] = []
    for definition in get_settings().achievements:
        for level, threshold in enumerate(definition.thresholds, start=1):
            if values[definition.metric] >= threshold and (definition.id, level) not in owned:
                new.append(
                    Badge(
                        user_id=user.id,
                        achievement_id=definition.id,
                        level=level,
                        earned_at=now,
                        lesson_attempt_id=attempt_id,
                    )
                )
    db.add_all(new)
    await db.flush()
    return [read for badge in new if (read := badge_read(badge)) is not None]


async def overview(db: AsyncSession, user: User) -> AchievementsRead:
    values = await metrics(db, user)
    badges = list(
        await db.scalars(
            select(Badge)
            .where(Badge.user_id == user.id)
            .order_by(Badge.earned_at.desc(), Badge.achievement_id, Badge.level)
        )
    )
    achievements = []
    for definition in get_settings().achievements:
        value = values[definition.metric]
        level = sum(1 for threshold in definition.thresholds if value >= threshold)
        achievements.append(
            AchievementRead(
                id=definition.id,
                metric=definition.metric,
                value=value,
                thresholds=list(definition.thresholds),
                level=level,
                next_threshold=(
                    definition.thresholds[level] if level < len(definition.thresholds) else None
                ),
            )
        )
    return AchievementsRead(
        achievements=achievements,
        badges=[read for badge in badges if (read := badge_read(badge)) is not None],
    )


async def badges_of_attempt(db: AsyncSession, attempt_id: uuid.UUID) -> list[BadgeRead]:
    rows = await db.scalars(
        select(Badge)
        .where(Badge.lesson_attempt_id == attempt_id)
        .order_by(Badge.achievement_id, Badge.level)
    )
    return [read for badge in rows if (read := badge_read(badge)) is not None]
