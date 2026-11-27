import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import ChallengeTemplate, get_settings
from tests.helpers import answer_for

pytestmark = pytest.mark.usefixtures("syllabus")


async def test_get_challenges_creates_today_and_month(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/challenges", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["daily"]) == 3
    assert [c["kind"] for c in data["monthly"]] == ["earn_xp"]
    assert all(c["progress"] == 0 and c["completed_at"] is None for c in data["daily"])
    again = (await client.get("/challenges", headers=auth_headers)).json()
    assert [c["id"] for c in again["daily"]] == [c["id"] for c in data["daily"]]


async def test_finishing_a_lesson_moves_the_challenges(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        get_settings(),
        "daily_challenges",
        [
            ChallengeTemplate(kind="complete_lessons", goal=1, reward_xp=10),
            ChallengeTemplate(kind="first_try_correct", goal=50, reward_xp=10),
            ChallengeTemplate(kind="perfect_lessons", goal=1, reward_xp=15),
        ],
    )
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

    data = (await client.get("/challenges", headers=auth_headers)).json()
    daily = {c["kind"]: c for c in data["daily"]}
    assert daily["complete_lessons"]["completed_at"] is not None
    assert daily["perfect_lessons"]["completed_at"] is not None
    assert daily["first_try_correct"]["progress"] == 5
    assert data["monthly"][0]["progress"] == 55  # la EXP de la lección
    me = (await client.get("/me", headers=auth_headers)).json()
    assert me["xp_total"] == 55 + 10 + 15


async def test_challenges_require_login(client: AsyncClient) -> None:
    response = await client.get("/challenges")
    assert response.status_code == 401
