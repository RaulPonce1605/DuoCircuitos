from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import LeagueGroup, LeagueMember, User, XpEvent
from app.services import auth as auth_service
from app.services import leagues

# Jueves 26 de noviembre de 2026; la semana empezó el lunes 23.
NOW = datetime(2026, 11, 26, 18, tzinfo=UTC)
LAST_WEEK = NOW - timedelta(days=7)


async def _users(db: AsyncSession, count: int, *, tier: int = 0) -> list[User]:
    users = []
    for i in range(count):
        session = await auth_service.register(
            db,
            email=f"liga{i}@example.com",
            password="contraseña-segura",
            display_name=f"Alumno {i}",
            timezone="UTC",
        )
        session.user.league_tier = tier
        users.append(session.user)
    await db.flush()
    return users


def _xp(db: AsyncSession, user: User, amount: int, when: datetime) -> None:
    db.add(XpEvent(user_id=user.id, amount=amount, source="lesson", created_at=when))


def test_week_starts_on_monday_utc() -> None:
    assert leagues.week_start(NOW) == date(2026, 11, 23)
    # Domingo 23:59 UTC sigue siendo la semana; lunes 00:00 ya es la siguiente.
    assert leagues.week_start(datetime(2026, 11, 29, 23, 59, tzinfo=UTC)) == date(2026, 11, 23)
    assert leagues.week_start(datetime(2026, 11, 30, tzinfo=UTC)) == date(2026, 11, 30)


@pytest.mark.parametrize(
    ("rank", "size", "tier", "xp", "expected"),
    [
        (1, 20, 0, 10, "promotion"),
        (5, 20, 0, 10, "promotion"),
        (6, 20, 0, 10, None),
        (20, 20, 0, 0, None),  # el nivel más bajo no baja
        (16, 20, 2, 10, "demotion"),
        (15, 20, 2, 10, None),
        (1, 20, 4, 99, None),  # el nivel más alto no sube
        (1, 20, 0, 0, None),  # sin EXP no se sube
        (5, 6, 1, 10, "promotion"),  # grupo chico: las zonas no se enciman
        (6, 6, 1, 10, "demotion"),
    ],
)
def test_zones(rank: int, size: int, tier: int, xp: int, expected: str | None) -> None:
    assert leagues.zone(rank, size, tier, xp) == expected


async def test_join_fills_groups_up_to_the_size(
    db: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "league_group_size", 2)
    users = await _users(db, 3)

    members = [await leagues.join(db, user, NOW) for user in users]
    again = await leagues.join(db, users[0], NOW)

    assert members[0].group_id == members[1].group_id != members[2].group_id
    assert again.group_id == members[0].group_id
    assert {m.week_start for m in members} == {date(2026, 11, 23)}


async def test_groups_are_per_tier(db: AsyncSession) -> None:
    low = (await _users(db, 1))[0]
    high = await auth_service.register(
        db, email="alta@example.com", password="contraseña-segura", display_name="A", timezone="UTC"
    )
    high.user.league_tier = 2

    first = await leagues.join(db, low, NOW)
    second = await leagues.join(db, high.user, NOW)

    assert first.group_id != second.group_id


async def test_standings_count_only_this_weeks_xp(db: AsyncSession) -> None:
    a, b = await _users(db, 2)
    await leagues.join(db, a, NOW)
    member = await leagues.join(db, b, NOW)
    _xp(db, a, 30, NOW)
    _xp(db, b, 50, NOW)
    _xp(db, a, 999, LAST_WEEK)  # de otra semana: no cuenta
    await db.flush()
    group = await db.get(LeagueGroup, member.group_id)
    assert group is not None

    rows = await leagues.standings(db, group)

    assert [(row.user.id, row.xp, row.rank) for row in rows] == [(b.id, 50, 1), (a.id, 30, 2)]


async def test_closing_last_week_moves_tiers_and_announces_once(
    db: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "league_promote_count", 1)
    monkeypatch.setattr(get_settings(), "league_demote_count", 1)
    users = await _users(db, 3, tier=1)
    for user, xp in zip(users, [100, 50, 10], strict=True):
        await leagues.join(db, user, LAST_WEEK)
        _xp(db, user, xp, LAST_WEEK)
    await db.flush()

    first = await leagues.overview(db, users[0], NOW)
    again = await leagues.overview(db, users[0], NOW)

    assert first.last_result is not None
    assert (first.last_result.result, first.last_result.final_rank) == ("promoted", 1)
    assert first.last_result.tier == 1
    assert again.last_result is None  # se anuncia una sola vez
    tiers = [await db.scalar(select(User.league_tier).where(User.id == user.id)) for user in users]
    assert tiers == [2, 1, 0]
    results = list(await db.scalars(select(LeagueMember.result).order_by(LeagueMember.final_rank)))
    assert results == ["promoted", "stayed", "demoted"]
    # Esta semana todavía no ha ganado EXP: no está en ningún grupo, pero ya en su nivel nuevo.
    assert first.joined is False
    assert first.tier == 2


async def test_overview_hides_private_names(db: AsyncSession) -> None:
    me, other = await _users(db, 2)
    other.profile_public = False
    me.profile_public = False
    for user in (me, other):
        await leagues.join(db, user, NOW)
        _xp(db, user, 10, NOW)
    await db.flush()

    data = await leagues.overview(db, me, NOW)

    names = {row.is_me: row.display_name for row in data.members}
    assert names == {True: "Alumno 0", False: None}  # el propio nombre sí se ve
    assert data.joined is True
    assert data.ends_at == datetime(2026, 11, 30, tzinfo=UTC)
