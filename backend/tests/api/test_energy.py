from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import auth as auth_service
from tests.helpers import answer_for

pytestmark = pytest.mark.usefixtures("syllabus")


async def test_me_and_start_report_full_energy(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    me = await client.get("/me", headers=auth_headers)
    started = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)

    full = {"current": 5, "max": 5, "next_refill_at": None}
    assert me.json()["energy"] == full
    assert started.json()["energy"] == full


async def test_a_mistake_spends_energy_and_a_correct_answer_does_not(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)
    instance_id = started.json()["current_exercise"]["instance_id"]

    wrong = await answer_for(db, instance_id, correct=False)
    after_wrong = (
        await client.post(
            f"/exercise-instances/{instance_id}/check", json={"answer": wrong}, headers=auth_headers
        )
    ).json()
    next_id = after_wrong["next_exercise"]["instance_id"]
    right = await answer_for(db, next_id, correct=True)
    after_right = (
        await client.post(
            f"/exercise-instances/{next_id}/check", json={"answer": right}, headers=auth_headers
        )
    ).json()

    assert after_wrong["energy"]["current"] == 4
    assert after_wrong["energy"]["next_refill_at"] is not None
    assert after_right["energy"]["current"] == 4
    me = await client.get("/me", headers=auth_headers)
    assert me.json()["energy"]["current"] == 4


async def test_without_energy_you_cannot_start_or_answer(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
) -> None:
    started = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)
    instance_id = started.json()["current_exercise"]["instance_id"]
    user_session.user.energy_used = 5
    user_session.user.energy_updated_at = datetime.now(UTC)
    await db.flush()

    answer = await answer_for(db, instance_id, correct=True)
    check = await client.post(
        f"/exercise-instances/{instance_id}/check", json={"answer": answer}, headers=auth_headers
    )
    start = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)

    assert check.status_code == 409
    assert check.json() == {"code": "not_enough_energy"}
    assert start.status_code == 409
    assert start.json() == {"code": "not_enough_energy"}
