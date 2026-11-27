from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import AchievementDefinition, get_settings
from app.models import Badge
from app.services import achievements
from app.services import auth as auth_service

NOW = datetime(2026, 11, 26, 12, tzinfo=UTC)


async def test_metrics_of_a_new_user_are_zero(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    values = await achievements.metrics(db, user_session.user)
    assert set(values.values()) == {0}


async def test_evaluate_gives_each_reached_level_once(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    user.streak_longest = 8
    user.streak_current = 8

    first = await achievements.evaluate(db, user, NOW)
    second = await achievements.evaluate(db, user, NOW)

    assert [(b.achievement_id, b.level, b.threshold) for b in first] == [
        ("streak", 1, 3),
        ("streak", 2, 7),
    ]
    assert second == []


async def test_badges_of_removed_achievements_are_hidden(
    db: AsyncSession, user_session: auth_service.Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = user_session.user
    db.add(Badge(user_id=user.id, achievement_id="viejo", level=1, earned_at=NOW))
    await db.flush()
    monkeypatch.setattr(
        get_settings(),
        "achievements",
        [AchievementDefinition(id="xp", metric="xp_total", thresholds=[10])],
    )

    overview = await achievements.overview(db, user)

    assert overview.badges == []
    assert [a.id for a in overview.achievements] == ["xp"]


@pytest.mark.parametrize("thresholds", [[], [0, 5], [5, 5], [10, 3]])
def test_thresholds_must_be_positive_and_increasing(thresholds: list[int]) -> None:
    with pytest.raises(ValidationError):
        AchievementDefinition(id="x", metric="xp_total", thresholds=thresholds)
