from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExerciseInstance, LessonAttempt
from tests.helpers import answer_for

pytestmark = pytest.mark.usefixtures("syllabus")

Json = dict[str, Any]


async def _start(client: AsyncClient, headers: dict[str, str], lesson: str = "ohm-01") -> Json:
    # Las lecciones también se inician por su nodo; la clave del nodo es el slug.
    url = f"/lessons/{lesson}/attempts" if ":" not in lesson else f"/nodes/{lesson}/attempts"
    response = await client.post(url, headers=headers)
    assert response.status_code == 201, response.text
    data: Json = response.json()
    return data


async def _check(
    client: AsyncClient, headers: dict[str, str], instance_id: str, answer: Json
) -> Json:
    response = await client.post(
        f"/exercise-instances/{instance_id}/check", json={"answer": answer}, headers=headers
    )
    assert response.status_code == 200, response.text
    data: Json = response.json()
    return data


async def _play(
    client: AsyncClient,
    db: AsyncSession,
    headers: dict[str, str],
    lesson: str = "ohm-01",
    *,
    fail_first: int = 0,
) -> Json:
    """Juega la lección completa; falla los primeros `fail_first` ejercicios una vez."""
    started = await _start(client, headers, lesson)
    current = started["current_exercise"]
    last: Json = {}
    failed = 0
    for _ in range(50):
        wrong = failed < fail_first
        answer = await answer_for(db, current["instance_id"], correct=not wrong)
        last = await _check(client, headers, current["instance_id"], answer)
        assert last["correct"] is not wrong
        failed += wrong
        if last["attempt_completed"]:
            break
        current = last["next_exercise"]
    assert last["attempt_completed"]
    return started | {"last": last}


# --- Iniciar ---------------------------------------------------------------------------------


async def test_start_lesson_returns_first_exercise_without_solution(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    response = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["lesson"] == {"slug": "ohm-01", "title": "Voltaje, corriente y resistencia"}
    assert data["progress"] == {"completed": 0, "total": 5}
    exercise = data["current_exercise"]["exercise"]
    assert exercise["type"] == "multiple_choice"
    assert sorted(exercise["options"]) == ["Ampere", "Ohm", "Volt", "Watt"]
    for secret in ["correcta", "correct", "explicacion", "explanation", "pistas", "solucion"]:
        assert secret not in response.text


async def test_numeric_prompt_has_values_but_not_the_result(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = await _start(client, auth_headers)
    first = started["current_exercise"]
    result = await _check(
        client,
        auth_headers,
        first["instance_id"],
        await answer_for(db, first["instance_id"], correct=True),
    )
    numeric = result["next_exercise"]
    # Solo viajan el enunciado ya resuelto y la unidad: ni fórmula, ni parámetros, ni resultado.
    assert set(numeric) == {"instance_id", "exercise"}
    assert set(numeric["exercise"]) == {"type", "prompt", "unit"}
    assert numeric["exercise"]["type"] == "numeric"
    assert numeric["exercise"]["unit"] == "A"
    assert "{" not in numeric["exercise"]["prompt"]
    assert "Q / (t * 60)" not in str(numeric)


async def test_locked_and_unknown_lessons(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    locked = await client.post("/lessons/ohm-02/attempts", headers=auth_headers)
    assert locked.status_code == 409
    assert locked.json() == {"code": "node_locked"}

    unknown = await client.post("/lessons/no-existe/attempts", headers=auth_headers)
    assert unknown.status_code == 404
    assert unknown.json() == {"code": "not_found"}


async def test_lesson_endpoints_require_auth(client: AsyncClient) -> None:
    assert (await client.post("/lessons/ohm-01/attempts")).status_code == 401
    some_id = "00000000-0000-0000-0000-000000000000"
    check = await client.post(
        f"/exercise-instances/{some_id}/check",
        json={"answer": {"type": "fill_pattern", "text": "R"}},
    )
    assert check.status_code == 401
    assert (await client.get(f"/lesson-attempts/{some_id}/summary")).status_code == 401


# --- Comprobar -------------------------------------------------------------------------------


async def test_correct_answer_advances(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = await _start(client, auth_headers)
    instance_id = started["current_exercise"]["instance_id"]

    result = await _check(
        client, auth_headers, instance_id, await answer_for(db, instance_id, correct=True)
    )

    assert result["correct"] is True
    assert result["correct_answer"] == "Ohm"
    assert result["explanation"]
    assert result["progress"] == {"completed": 1, "total": 5}
    assert result["attempt_completed"] is False
    assert result["next_exercise"]["instance_id"] != instance_id


async def test_wrong_answer_is_requeued_at_the_end(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = await _start(client, auth_headers)
    instance_id = started["current_exercise"]["instance_id"]

    result = await _check(
        client, auth_headers, instance_id, await answer_for(db, instance_id, correct=False)
    )

    assert result["correct"] is False
    assert result["correct_answer"] == "Ohm"
    assert result["progress"] == {"completed": 0, "total": 5}
    instances = (
        await db.scalars(
            select(ExerciseInstance)
            .join(LessonAttempt)
            .where(LessonAttempt.id == started["attempt_id"])
            .order_by(ExerciseInstance.position)
        )
    ).all()
    assert len(instances) == 6
    assert instances[-1].is_retry and instances[-1].exercise_id == instances[0].exercise_id


async def test_answer_twice_out_of_order_or_foreign(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = await _start(client, auth_headers)
    first = started["current_exercise"]["instance_id"]
    answer = await answer_for(db, first, correct=True)
    result = await _check(client, auth_headers, first, answer)

    again = await client.post(
        f"/exercise-instances/{first}/check", json={"answer": answer}, headers=auth_headers
    )
    assert again.status_code == 409 and again.json() == {"code": "already_answered"}

    # Saltarse el siguiente: se intenta responder el tercero.
    third = (
        await db.scalars(
            select(ExerciseInstance.id).where(
                ExerciseInstance.attempt_id == started["attempt_id"],
                ExerciseInstance.position == 2,
            )
        )
    ).one()
    skip = await client.post(
        f"/exercise-instances/{third}/check",
        json={"answer": await answer_for(db, third, correct=True)},
        headers=auth_headers,
    )
    assert skip.status_code == 409 and skip.json() == {"code": "not_current_exercise"}

    other = await client.post(
        "/auth/register",
        json={"email": "otra@example.com", "password": "contraseña-segura", "display_name": "Otra"},
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
    nxt = result["next_exercise"]["instance_id"]
    foreign = await client.post(
        f"/exercise-instances/{nxt}/check",
        json={"answer": await answer_for(db, nxt, correct=True)},
        headers=other_headers,
    )
    assert foreign.status_code == 404


async def test_wrong_answer_type_is_422_and_not_recorded(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    started = await _start(client, auth_headers)
    instance_id = started["current_exercise"]["instance_id"]  # opción múltiple

    response = await client.post(
        f"/exercise-instances/{instance_id}/check",
        json={"answer": {"type": "fill_pattern", "text": "Ohm"}},
        headers=auth_headers,
    )

    assert response.status_code == 422 and response.json() == {"code": "invalid_answer"}
    instance = await db.get(ExerciseInstance, instance_id, populate_existing=True)
    assert instance is not None and instance.answered_at is None


@pytest.mark.parametrize(
    "body",
    [{}, {"answer": {"type": "otro"}}, {"answer": {"type": "multiple_choice", "option": -1}}],
)
async def test_malformed_check_body(
    client: AsyncClient, auth_headers: dict[str, str], body: Json
) -> None:
    started = await _start(client, auth_headers)
    response = await client.post(
        f"/exercise-instances/{started['current_exercise']['instance_id']}/check",
        json=body,
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


# --- Terminar --------------------------------------------------------------------------------


async def test_perfect_lesson_rewards_and_unlocks_next(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    played = await _play(client, db, auth_headers)
    assert played["last"]["progress"] == {"completed": 5, "total": 5}
    assert played["last"]["next_exercise"] is None

    summary = await client.get(
        f"/lesson-attempts/{played['attempt_id']}/summary", headers=auth_headers
    )
    assert summary.status_code == 200
    data = summary.json()
    assert (data["xp_awarded"], data["accuracy"], data["first_try_correct"]) == (55, 100, 5)
    assert data["streak"] == 1 and data["streak_extended"] is True
    assert "Corriente eléctrica" in data["concepts"]

    me = (await client.get("/me", headers=auth_headers)).json()
    assert (me["xp_total"], me["streak_current"], me["streak_longest"]) == (55, 1, 1)

    path = (await client.get("/path", headers=auth_headers)).json()
    nodes = path["stages"][0]["sections"][0]["units"][0]["nodes"]
    assert nodes[0]["status"] == "completed"
    assert nodes[1]["status"] == "available" and nodes[1]["is_current"]


async def test_lesson_with_mistakes(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    played = await _play(client, db, auth_headers, fail_first=1)

    summary = (
        await client.get(f"/lesson-attempts/{played['attempt_id']}/summary", headers=auth_headers)
    ).json()
    assert (summary["xp_awarded"], summary["accuracy"], summary["first_try_correct"]) == (45, 80, 4)


async def test_summary_before_completion_and_of_other_user(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    started = await _start(client, auth_headers)
    early = await client.get(
        f"/lesson-attempts/{started['attempt_id']}/summary", headers=auth_headers
    )
    assert early.status_code == 409 and early.json() == {"code": "attempt_not_completed"}

    other = await client.post(
        "/auth/register",
        json={"email": "otra@example.com", "password": "contraseña-segura", "display_name": "Otra"},
    )
    foreign = await client.get(
        f"/lesson-attempts/{started['attempt_id']}/summary",
        headers={"Authorization": f"Bearer {other.json()['access_token']}"},
    )
    assert foreign.status_code == 404


async def test_repeating_a_lesson_counts_again_but_streak_once_per_day(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    await _play(client, db, auth_headers)
    second = await _play(client, db, auth_headers)

    summary = (
        await client.get(f"/lesson-attempts/{second['attempt_id']}/summary", headers=auth_headers)
    ).json()
    assert summary["streak_extended"] is False
    me = (await client.get("/me", headers=auth_headers)).json()
    assert me["xp_total"] == 110 and me["streak_current"] == 1


async def test_whole_path_can_be_completed_in_order(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    """Recorre el temario real en orden: lecciones, repasos, cofres y evaluaciones. Cada nodo se
    desbloquea al terminar el anterior y todos se pueden completar."""
    path = (await client.get("/path", headers=auth_headers)).json()
    nodes = [
        node
        for stage in path["stages"]
        for section in stage["sections"]
        for unit in section["units"]
        for node in unit["nodes"]
    ]
    assert [node["type"] for node in nodes[:5]] == [
        "lesson",
        "lesson",
        "review",
        "chest",
        "assessment",
    ]
    xp = 0
    for node in nodes:
        if node["type"] == "chest":
            opened = await client.post(f"/nodes/{node['key']}/chest", headers=auth_headers)
            assert opened.status_code == 200, opened.text
            xp += opened.json()["reward"]["xp"]
            continue
        played = await _play(client, db, auth_headers, node["key"])
        assert played["node"]["type"] == node["type"]
        xp += 10 * played["progress"]["total"] + 5  # todo al primer intento + bono perfecto

    me = (await client.get("/me", headers=auth_headers)).json()
    assert me["xp_total"] == xp
    path = (await client.get("/path", headers=auth_headers)).json()
    statuses = {
        node["status"]
        for stage in path["stages"]
        for section in stage["sections"]
        for unit in section["units"]
        for node in unit["nodes"]
    }
    assert statuses == {"completed"}
