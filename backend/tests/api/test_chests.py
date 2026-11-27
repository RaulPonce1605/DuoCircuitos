from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import XpEvent
from app.services import auth as auth_service
from tests.helpers import answer_for

pytestmark = pytest.mark.usefixtures("syllabus")

Json = dict[str, Any]


async def _finish(
    client: AsyncClient,
    db: AsyncSession,
    headers: dict[str, str],
    key: str,
    *,
    fail_first: bool = False,
) -> Json:
    """Juega un nodo hasta terminarlo y devuelve su resumen."""
    url = f"/nodes/{key}/attempts"
    started = (await client.post(url, headers=headers)).json()
    current = started["current_exercise"]
    failed = False
    while True:
        wrong = fail_first and not failed
        answer = await answer_for(db, current["instance_id"], correct=not wrong)
        result = (
            await client.post(
                f"/exercise-instances/{current['instance_id']}/check",
                json={"answer": answer},
                headers=headers,
            )
        ).json()
        failed = failed or wrong
        if result["attempt_completed"]:
            break
        current = result["next_exercise"]
    summary = await client.get(f"/lesson-attempts/{started['attempt_id']}/summary", headers=headers)
    assert summary.status_code == 200, summary.text
    data: Json = summary.json()
    return data


async def test_finishing_a_lesson_leaves_a_closed_chest_and_first_badges(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    summary = await _finish(client, db, auth_headers, "ohm-01")

    assert summary["chest_id"] is not None
    earned = {(badge["achievement_id"], badge["level"]) for badge in summary["new_badges"]}
    assert earned == {("lessons", 1), ("perfect", 1)}


async def test_opening_a_lesson_chest_gives_xp_and_energy_once(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    summary = await _finish(client, db, auth_headers, "ohm-01", fail_first=True)
    xp_before = (await client.get("/me", headers=auth_headers)).json()["xp_total"]

    first = await client.post(f"/chests/{summary['chest_id']}/open", headers=auth_headers)
    second = await client.post(f"/chests/{summary['chest_id']}/open", headers=auth_headers)

    assert first.status_code == 200
    reward = first.json()["reward"]
    assert 2 <= reward["xp"] <= 10
    assert reward["energy"] == 1
    assert first.json()["energy"]["current"] == 5  # el fallo gastó 1 y el cofre la devolvió
    assert first.json()["new_badges"] == [
        {
            "achievement_id": "chests",
            "level": 1,
            "threshold": 1,
            "earned_at": first.json()["new_badges"][0]["earned_at"],
        }
    ]
    # Abrirlo otra vez devuelve el mismo premio y no da más.
    assert second.json()["reward"] == reward
    assert second.json()["new_badges"] == []
    me = (await client.get("/me", headers=auth_headers)).json()
    assert me["xp_total"] == xp_before + reward["xp"]
    chest_events = await db.scalar(
        select(func.count()).where(XpEvent.source == "chest", XpEvent.amount == reward["xp"])
    )
    assert chest_events == 1


async def test_another_users_chest_is_not_found(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    summary = await _finish(client, db, auth_headers, "ohm-01")
    other = await auth_service.register(
        db,
        email="otro@example.com",
        password="contraseña-segura",
        display_name="Otro",
        timezone="UTC",
    )

    response = await client.post(
        f"/chests/{summary['chest_id']}/open",
        headers={"Authorization": f"Bearer {other.access_token}"},
    )

    assert response.status_code == 404


async def test_the_path_chest_opens_once_and_completes_the_node(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    key = "u01-ley-de-ohm:chest:1"
    locked = await client.post(f"/nodes/{key}/chest", headers=auth_headers)
    for node in ["ohm-01", "ohm-02", "u01-ley-de-ohm:review:1"]:
        await _finish(client, db, auth_headers, node)

    first = await client.post(f"/nodes/{key}/chest", headers=auth_headers)
    again = await client.post(f"/nodes/{key}/chest", headers=auth_headers)
    not_a_chest = await client.post("/nodes/ohm-01/chest", headers=auth_headers)
    play_chest = await client.post(f"/nodes/{key}/attempts", headers=auth_headers)

    assert locked.status_code == 409
    assert locked.json() == {"code": "node_locked"}
    assert first.status_code == 200
    assert first.json()["source"] == "node"
    assert 15 <= first.json()["reward"]["xp"] <= 30
    assert again.json()["reward"] == first.json()["reward"]
    assert not_a_chest.json() == {"code": "not_a_chest"}
    assert play_chest.json() == {"code": "node_not_playable"}
    path = (await client.get("/path", headers=auth_headers)).json()
    nodes = {
        node["key"]: node["status"]
        for unit in path["stages"][0]["sections"][0]["units"]
        for node in unit["nodes"]
    }
    assert nodes[key] == "completed"
    assert nodes["u01-ley-de-ohm:assessment:1"] == "available"


async def test_achievements_overview(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    empty = (await client.get("/me/achievements", headers=auth_headers)).json()
    await _finish(client, db, auth_headers, "ohm-01")
    after = (await client.get("/me/achievements", headers=auth_headers)).json()

    lessons = next(a for a in empty["achievements"] if a["id"] == "lessons")
    assert lessons == {
        "id": "lessons",
        "metric": "lessons_completed",
        "value": 0,
        "thresholds": [1, 5, 10],
        "level": 0,
        "next_threshold": 1,
    }
    assert empty["badges"] == []
    lessons = next(a for a in after["achievements"] if a["id"] == "lessons")
    assert (lessons["value"], lessons["level"], lessons["next_threshold"]) == (1, 1, 5)
    assert {b["achievement_id"] for b in after["badges"]} == {"lessons", "perfect"}


async def test_achievements_require_login(client: AsyncClient) -> None:
    response = await client.get("/me/achievements")
    assert response.status_code == 401
