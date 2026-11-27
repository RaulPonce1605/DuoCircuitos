import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import answer_for

pytestmark = pytest.mark.usefixtures("syllabus")


async def test_before_earning_xp_you_are_not_in_a_league(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/leagues/current", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["joined"] is False
    assert data["members"] == []
    assert (data["tier"], data["tier_id"]) == (0, "resistor")
    assert data["tiers"][0] == "resistor"
    me = (await client.get("/me", headers=auth_headers)).json()
    assert (me["league_tier"], me["league_tier_id"]) == (0, "resistor")


async def test_finishing_a_lesson_joins_the_league_with_its_xp(
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

    data = (await client.get("/leagues/current", headers=auth_headers)).json()

    assert data["joined"] is True
    assert data["members"] == [
        {"rank": 1, "display_name": "Alumna", "xp": 55, "is_me": True, "zone": "promotion"}
    ]


async def test_league_requires_login(client: AsyncClient) -> None:
    response = await client.get("/leagues/current")
    assert response.status_code == 401
