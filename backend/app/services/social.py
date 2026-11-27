"""Amigos y seguidores (docs/diseno/amigos.md).

- Seguir es en un solo sentido; dos alumnos que se siguen entre sí son amigos.
- Solo se encuentran y se pueden seguir los perfiles públicos (Configuración → Privacidad).
- Si alguien con perfil privado te sigue, aparece en tus seguidores sin nombre.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Follow, User
from app.schemas.social import FriendsRead, UserCardRead
from app.services.errors import CannotFollowSelf, NotFound
from app.services.gamification import effective_streak

SEARCH_LIMIT = 20
MIN_QUERY = 2


async def _relations(
    db: AsyncSession, me: User, others: list[uuid.UUID]
) -> tuple[set[uuid.UUID], set[uuid.UUID]]:
    """A quiénes de `others` sigo y quiénes me siguen."""
    if not others:
        return set(), set()
    following = set(
        await db.scalars(
            select(Follow.followee_id).where(
                Follow.follower_id == me.id, Follow.followee_id.in_(others)
            )
        )
    )
    followers = set(
        await db.scalars(
            select(Follow.follower_id).where(
                Follow.followee_id == me.id, Follow.follower_id.in_(others)
            )
        )
    )
    return following, followers


def _card(
    user: User, following: set[uuid.UUID], followers: set[uuid.UUID], now: datetime
) -> UserCardRead:
    tiers = get_settings().league_tiers
    tier = min(user.league_tier or 0, len(tiers) - 1)
    return UserCardRead(
        id=user.id,
        display_name=user.display_name if user.profile_public else None,
        xp_total=user.xp_total,
        streak=effective_streak(user, now),
        league_tier=tier,
        league_tier_id=tiers[tier],
        is_following=user.id in following,
        follows_me=user.id in followers,
    )


async def _cards(db: AsyncSession, me: User, users: list[User]) -> list[UserCardRead]:
    now = datetime.now(UTC)
    following, followers = await _relations(db, me, [user.id for user in users])
    return [_card(user, following, followers, now) for user in users]


async def search(db: AsyncSession, me: User, query: str) -> list[UserCardRead]:
    """Perfiles públicos cuyo nombre contiene `query` (sin distinguir mayúsculas)."""
    text = query.strip()
    if len(text) < MIN_QUERY:
        return []
    pattern = "%" + text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    users = list(
        await db.scalars(
            select(User)
            .where(
                User.id != me.id,
                User.profile_public.is_(True),
                func.lower(User.display_name).like(func.lower(pattern), escape="\\"),
            )
            .order_by(User.xp_total.desc(), User.display_name)
            .limit(SEARCH_LIMIT)
        )
    )
    return await _cards(db, me, users)


async def friends(db: AsyncSession, me: User) -> FriendsRead:
    following = list(
        await db.scalars(
            select(User)
            .join(Follow, Follow.followee_id == User.id)
            .where(Follow.follower_id == me.id)
            .order_by(User.xp_total.desc(), User.display_name)
        )
    )
    followers = list(
        await db.scalars(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.followee_id == me.id)
            .order_by(User.xp_total.desc(), User.display_name)
        )
    )
    return FriendsRead(
        following=await _cards(db, me, following), followers=await _cards(db, me, followers)
    )


async def _public_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await db.get(User, user_id)
    if user is None or not user.profile_public:
        raise NotFound  # un perfil privado no se puede encontrar ni seguir
    return user


async def follow(db: AsyncSession, me: User, user_id: uuid.UUID) -> UserCardRead:
    if user_id == me.id:
        raise CannotFollowSelf
    other = await _public_user(db, user_id)
    await db.execute(
        insert(Follow)
        .values(follower_id=me.id, followee_id=other.id)
        .on_conflict_do_nothing(index_elements=["follower_id", "followee_id"])
    )
    await db.commit()
    return (await _cards(db, me, [other]))[0]


async def unfollow(db: AsyncSession, me: User, user_id: uuid.UUID) -> UserCardRead:
    other = await db.get(User, user_id)
    if other is None:
        raise NotFound
    await db.execute(
        delete(Follow).where(Follow.follower_id == me.id, Follow.followee_id == other.id)
    )
    await db.commit()
    return (await _cards(db, me, [other]))[0]
