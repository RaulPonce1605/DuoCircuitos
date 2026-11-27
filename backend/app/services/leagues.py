"""Ligas semanales (docs/diseno/ligas.md). El backend es la fuente de verdad (CLAUDE.md 5.4).

- La semana va de lunes a lunes en UTC (la misma para todos, para que los grupos compitan en el
  mismo periodo).
- Un alumno entra a la liga de la semana la primera vez que gana EXP en ella: se le asigna un
  grupo de su nivel con lugar libre (o uno nuevo) de hasta `LEAGUE_GROUP_SIZE`.
- La EXP de la semana no se guarda aparte: se suma de `xp_events`.
- Cierre automático sin tareas programadas: la primera vez que alguien del grupo vuelve después
  de que terminó la semana, el grupo se cierra. Los primeros suben de nivel y los últimos bajan.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Literal

from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import LeagueGroup, LeagueMember, User, XpEvent
from app.schemas.leagues import LeagueMemberRead, LeagueRead, LeagueResultRead
from app.services.errors import NotFound

Zone = Literal["promotion", "demotion"]
Result = Literal["promoted", "stayed", "demoted"]


def week_start(now: datetime) -> date:
    today = now.astimezone(UTC).date()
    return today - timedelta(days=today.weekday())


def week_bounds(start: date) -> tuple[datetime, datetime]:
    begin = datetime.combine(start, time.min, tzinfo=UTC)
    return begin, begin + timedelta(days=7)


def max_tier() -> int:
    return len(get_settings().league_tiers) - 1


@dataclass(frozen=True)
class Standing:
    member: LeagueMember
    user: User
    xp: int
    rank: int


async def standings(db: AsyncSession, group: LeagueGroup) -> list[Standing]:
    """El ranking del grupo: más EXP de la semana primero; en empate, quien entró antes."""
    begin, end = week_bounds(group.week_start)
    xp = func.coalesce(func.sum(XpEvent.amount), 0)
    rows = await db.execute(
        select(LeagueMember, User, xp)
        .join(User, User.id == LeagueMember.user_id)
        .outerjoin(
            XpEvent,
            and_(
                XpEvent.user_id == LeagueMember.user_id,
                XpEvent.created_at >= begin,
                XpEvent.created_at < end,
            ),
        )
        .where(LeagueMember.group_id == group.id)
        .group_by(LeagueMember.group_id, LeagueMember.user_id, User.id)
        .order_by(xp.desc(), LeagueMember.joined_at, LeagueMember.user_id)
    )
    return [
        Standing(member=member, user=user, xp=int(total), rank=rank)
        for rank, (member, user, total) in enumerate(rows, start=1)
    ]


def zone(rank: int, size: int, tier: int, xp: int) -> Zone | None:
    """Zona del lugar `rank` en un grupo de `size`: sube, baja o se queda.

    Para subir hay que haber ganado EXP. Las zonas nunca se enciman: en un grupo chico se
    reparten los lugares entre subir y bajar sin que nadie esté en las dos.
    """
    settings = get_settings()
    promote = min(settings.league_promote_count, size)
    if rank <= promote and tier < max_tier() and xp > 0:
        return "promotion"
    demote_from = max(promote, size - settings.league_demote_count)
    if rank > demote_from and tier > 0:
        return "demotion"
    return None


async def close_group(db: AsyncSession, group: LeagueGroup, now: datetime) -> None:
    """Cierra un grupo de una semana que ya terminó: guarda lugares y cambia de nivel."""
    locked = await db.scalar(
        select(LeagueGroup)
        .where(LeagueGroup.id == group.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if locked is None or locked.closed_at is not None:
        return
    rows = await standings(db, locked)
    for row in rows:
        where = zone(row.rank, len(rows), locked.tier, row.xp)
        result: Result = (
            "promoted" if where == "promotion" else "demoted" if where == "demotion" else "stayed"
        )
        row.member.final_rank = row.rank
        row.member.final_xp = row.xp
        row.member.result = result
        # El nivel nuevo sale del nivel del grupo, no del actual del alumno: así cerrar dos
        # veces o en otro orden da lo mismo.
        delta = {"promoted": 1, "demoted": -1, "stayed": 0}[result]
        row.user.league_tier = min(max(locked.tier + delta, 0), max_tier())
    locked.closed_at = now
    await db.flush()


async def _close_past_weeks(db: AsyncSession, user: User, now: datetime) -> None:
    groups = await db.scalars(
        select(LeagueGroup)
        .join(LeagueMember, LeagueMember.group_id == LeagueGroup.id)
        .where(
            LeagueMember.user_id == user.id,
            LeagueGroup.week_start < week_start(now),
            LeagueGroup.closed_at.is_(None),
        )
        .order_by(LeagueGroup.week_start)
    )
    for group in list(groups):
        await close_group(db, group, now)
    await db.refresh(user)


async def current_membership(db: AsyncSession, user: User, now: datetime) -> LeagueMember | None:
    return await db.scalar(
        select(LeagueMember).where(
            LeagueMember.user_id == user.id, LeagueMember.week_start == week_start(now)
        )
    )


async def join(db: AsyncSession, user: User, now: datetime) -> LeagueMember:
    """Mete al alumno a la liga de esta semana (si no está). La fila del usuario debe estar
    bloqueada. Se llama cada vez que gana EXP."""
    existing = await current_membership(db, user, now)
    if existing is not None:
        return existing
    await _close_past_weeks(db, user, now)
    start = week_start(now)
    tier = min(user.league_tier, max_tier())
    # Un solo alumno a la vez busca lugar en los grupos de esta semana y nivel.
    await db.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
        {"key": f"league:{start.isoformat()}:{tier}"},
    )
    size = func.count(LeagueMember.user_id)
    group = await db.scalar(
        select(LeagueGroup)
        .outerjoin(LeagueMember, LeagueMember.group_id == LeagueGroup.id)
        .where(LeagueGroup.week_start == start, LeagueGroup.tier == tier)
        .group_by(LeagueGroup.id)
        .having(size < get_settings().league_group_size)
        .order_by(LeagueGroup.created_at, LeagueGroup.id)
        .limit(1)
    )
    if group is None:
        group = LeagueGroup(id=uuid.uuid4(), week_start=start, tier=tier)
        db.add(group)
        await db.flush()
    member = LeagueMember(group_id=group.id, user_id=user.id, week_start=start, joined_at=now)
    db.add(member)
    await db.flush()
    return member


async def overview(db: AsyncSession, user: User, now: datetime) -> LeagueRead:
    await db.refresh(user, with_for_update=True)
    await _close_past_weeks(db, user, now)
    settings = get_settings()
    start = week_start(now)
    _, end = week_bounds(start)

    last = await db.scalar(
        select(LeagueMember)
        .where(
            LeagueMember.user_id == user.id,
            LeagueMember.result.is_not(None),
            LeagueMember.result_seen_at.is_(None),
        )
        .order_by(LeagueMember.week_start.desc())
        .limit(1)
    )
    last_result = None
    if last is not None and last.result is not None:
        last_group = await db.get(LeagueGroup, last.group_id)
        if last_group is None:  # pragma: no cover - la llave foránea lo impide
            raise NotFound
        last_result = LeagueResultRead(
            week_start=last.week_start,
            tier=last_group.tier,
            result=last.result,
            final_rank=last.final_rank or 0,
            final_xp=last.final_xp or 0,
        )
        last.result_seen_at = now

    members: list[LeagueMemberRead] = []
    membership = await current_membership(db, user, now)
    tier = min(user.league_tier, max_tier())
    if membership is not None:
        group = await db.get(LeagueGroup, membership.group_id)
        if group is None:  # pragma: no cover - la llave foránea lo impide
            raise NotFound
        tier = group.tier
        rows = await standings(db, group)
        members = [
            LeagueMemberRead(
                rank=row.rank,
                # Un perfil privado se muestra sin nombre a los demás.
                display_name=(
                    row.user.display_name
                    if row.user.profile_public or row.user.id == user.id
                    else None
                ),
                xp=row.xp,
                is_me=row.user.id == user.id,
                zone=zone(row.rank, len(rows), group.tier, row.xp),
            )
            for row in rows
        ]
    await db.commit()
    return LeagueRead(
        tier=tier,
        tier_id=settings.league_tiers[tier],
        tiers=list(settings.league_tiers),
        week_start=start,
        ends_at=end,
        joined=membership is not None,
        members=members,
        group_size=settings.league_group_size,
        last_result=last_result,
    )
