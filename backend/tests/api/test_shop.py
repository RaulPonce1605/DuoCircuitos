from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import StreakFreezeUse
from app.services import auth as auth_service
from tests.helpers import answer_for

pytestmark = pytest.mark.usefixtures("syllabus")


async def test_shop_lists_items_and_coins(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/shop", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["coins"] == 0
    assert [(i["id"], i["price"]) for i in data["items"]] == [
        ("energy_refill", 60),
        ("streak_freeze", 150),
    ]
    me = (await client.get("/me", headers=auth_headers)).json()
    assert (me["coins"], me["streak_freezes"]) == (0, 0)


async def test_buy_with_coins_and_errors(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
) -> None:
    poor = await client.post("/shop/items/streak_freeze/buy", headers=auth_headers)
    unknown = await client.post("/shop/items/gemas/buy", headers=auth_headers)
    user_session.user.coins = 200
    await db.flush()
    bought = await client.post("/shop/items/streak_freeze/buy", headers=auth_headers)

    assert poor.status_code == 409
    assert poor.json() == {"code": "not_enough_coins"}
    assert unknown.status_code == 422
    assert bought.status_code == 200
    assert (bought.json()["coins"], bought.json()["streak_freezes"]) == (50, 1)


async def test_opening_a_chest_gives_coins(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = (await client.post("/lessons/ohm-01/attempts", headers=auth_headers)).json()
    current = started["current_exercise"]
    while True:
        answer = await answer_for(db, current["instance_id"], correct=True)
        result = (
            await client.post(
                f"/exercise-instances/{current['instance_id']}/check",
                json={"answer": answer},
                headers=auth_headers,
            )
        ).json()
        if result["attempt_completed"]:
            break
        current = result["next_exercise"]
    summary = (
        await client.get(f"/lesson-attempts/{started['attempt_id']}/summary", headers=auth_headers)
    ).json()

    opened = (await client.post(f"/chests/{summary['chest_id']}/open", headers=auth_headers)).json()

    assert 5 <= opened["reward"]["coins"] <= 15
    me = (await client.get("/me", headers=auth_headers)).json()
    assert me["coins"] == opened["reward"]["coins"]


async def test_a_freeze_saves_the_streak_when_finishing_a_lesson(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
) -> None:
    user = user_session.user
    today = (await client.get("/me", headers=auth_headers)).json()  # crea la sesión
    assert today["streak_current"] == 0
    from datetime import UTC, datetime

    from app.services.gamification import local_date

    local_today = local_date(datetime.now(UTC), user.timezone)
    user.streak_current = 4
    user.streak_longest = 4
    user.streak_last_date = local_today - timedelta(days=2)  # faltó ayer
    user.streak_freezes = 1
    await db.flush()

    assert (await client.get("/me", headers=auth_headers)).json()["streak_current"] == 4
    started = (await client.post("/lessons/ohm-01/attempts", headers=auth_headers)).json()
    current = started["current_exercise"]
    while True:
        answer = await answer_for(db, current["instance_id"], correct=True)
        result = (
            await client.post(
                f"/exercise-instances/{current['instance_id']}/check",
                json={"answer": answer},
                headers=auth_headers,
            )
        ).json()
        if result["attempt_completed"]:
            break
        current = result["next_exercise"]

    me = (await client.get("/me", headers=auth_headers)).json()
    assert (me["streak_current"], me["streak_freezes"]) == (5, 0)
    used = list(await db.scalars(select(StreakFreezeUse.day)))
    assert used == [local_today - timedelta(days=1)]
    assert isinstance(used[0], date)
