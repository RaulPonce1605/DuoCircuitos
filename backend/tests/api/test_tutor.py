from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Exercise, ExerciseInstance, TutorMessage
from app.services import auth as auth_service
from app.services.exercises import get_validator
from app.services.exercises.numeric import correct_value
from app.services.exercises.units import format_quantity
from app.services.tutor import TutorPrompt, TutorProvider, TutorProviderError
from tests.helpers import FakeTutorProvider, answer_for

pytestmark = pytest.mark.usefixtures("syllabus")

Json = dict[str, Any]
UseProvider = Callable[[TutorProvider | None], None]


async def _numeric_instance(
    client: AsyncClient, db: AsyncSession, headers: dict[str, str]
) -> tuple[str, ExerciseInstance]:
    """Avanza ohm-01 hasta su primer ejercicio numérico y devuelve esa instancia."""
    response = await client.post("/lessons/ohm-01/attempts", headers=headers)
    current = response.json()["current_exercise"]
    while current["exercise"]["type"] != "numeric":
        answer = await answer_for(db, current["instance_id"], correct=True)
        result = await client.post(
            f"/exercise-instances/{current['instance_id']}/check",
            json={"answer": answer},
            headers=headers,
        )
        current = result.json()["next_exercise"]
    instance = await db.scalar(
        select(ExerciseInstance)
        .where(ExerciseInstance.id == current["instance_id"])
        .execution_options(populate_existing=True)
    )
    assert instance is not None
    return current["instance_id"], instance


async def _result_text(db: AsyncSession, instance: ExerciseInstance) -> str:
    exercise = await db.get(Exercise, instance.exercise_id)
    assert exercise is not None
    validator = get_validator(exercise.type)
    spec = validator.parse_spec(exercise.spec)
    return format_quantity(correct_value(spec, instance.state), spec.unit)


async def _ask(
    client: AsyncClient, headers: dict[str, str], instance_id: str, message: str | None = None
) -> Json:
    response = await client.post(
        f"/exercise-instances/{instance_id}/tutor", json={"message": message}, headers=headers
    )
    assert response.status_code == 200, response.text
    data: Json = response.json()
    return data


async def test_without_provider_the_tutor_gives_the_syllabus_hints_in_order(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
) -> None:
    use_tutor_provider(None)
    instance_id, instance = await _numeric_instance(client, db, auth_headers)
    exercise = await db.get(Exercise, instance.exercise_id)
    assert exercise is not None

    first = await _ask(client, auth_headers, instance_id)
    second = await _ask(client, auth_headers, instance_id, "no entiendo")
    third = await _ask(client, auth_headers, instance_id)

    assert first == {
        "reply": exercise.hints[0],
        "source": "hint",
        "help_level": 1,
        "remaining_requests": get_settings().tutor_requests_per_exercise - 1,
    }
    assert second["reply"] == exercise.hints[1]
    assert third["reply"] == exercise.hints[-1]  # sin más pistas, repite la última
    assert third["help_level"] == 3


async def test_a_safe_llm_reply_reaches_the_student_and_keeps_the_history(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
) -> None:
    provider = FakeTutorProvider(lambda _: "Piensa en cuántos segundos tiene un minuto.")
    use_tutor_provider(provider)
    instance_id, _ = await _numeric_instance(client, db, auth_headers)

    first = await _ask(client, auth_headers, instance_id, "¿por dónde empiezo?")
    await _ask(client, auth_headers, instance_id, "¿y luego?")

    assert first["reply"] == "Piensa en cuántos segundos tiene un minuto."
    assert first["source"] == "llm"
    last_prompt = provider.prompts[-1]
    assert [(m.role, m.content) for m in last_prompt.messages] == [
        ("user", "¿por dónde empiezo?"),
        ("assistant", "Piensa en cuántos segundos tiene un minuto."),
        ("user", "¿y luego?"),
    ]
    saved = list(
        await db.scalars(
            select(TutorMessage.role).where(TutorMessage.exercise_instance_id == instance_id)
        )
    )
    assert sorted(saved) == ["student", "student", "tutor", "tutor"]


async def test_a_leaking_llm_reply_is_replaced_by_the_hint(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
) -> None:
    instance_id, instance = await _numeric_instance(client, db, auth_headers)
    result = await _result_text(db, instance)
    use_tutor_provider(FakeTutorProvider(lambda _: f"Fácil: la respuesta es {result}."))

    reply = await _ask(client, auth_headers, instance_id, "dime el resultado")

    assert result not in reply["reply"]
    assert reply["source"] == "hint"
    stored = await db.scalar(
        select(TutorMessage.content).where(
            TutorMessage.exercise_instance_id == instance_id, TutorMessage.role == "tutor"
        )
    )
    assert stored is not None and result not in stored


async def test_a_failing_provider_falls_back_to_the_hint(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
) -> None:
    def _fail(_: TutorPrompt) -> str:
        raise TutorProviderError("sin red")

    use_tutor_provider(FakeTutorProvider(_fail))
    instance_id, _ = await _numeric_instance(client, db, auth_headers)

    reply = await _ask(client, auth_headers, instance_id)

    assert reply["source"] == "hint"


async def test_limit_per_exercise(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "tutor_requests_per_exercise", 2)
    use_tutor_provider(None)
    instance_id, _ = await _numeric_instance(client, db, auth_headers)
    await _ask(client, auth_headers, instance_id)
    last = await _ask(client, auth_headers, instance_id)

    response = await client.post(
        f"/exercise-instances/{instance_id}/tutor", json={}, headers=auth_headers
    )

    assert last["remaining_requests"] == 0
    assert response.status_code == 429
    assert response.json() == {"code": "tutor_exercise_limit"}


async def test_limit_per_hour_counts_only_the_last_hour(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
    use_tutor_provider: UseProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "tutor_requests_per_hour", 1)
    use_tutor_provider(None)
    instance_id, _ = await _numeric_instance(client, db, auth_headers)
    old = TutorMessage(
        user_id=user_session.user.id,
        exercise_instance_id=instance_id,
        role="tutor",
        content="pista vieja",
        source="hint",
        created_at=datetime.now(UTC) - timedelta(hours=2),
    )
    db.add(old)
    await db.flush()

    await _ask(client, auth_headers, instance_id)  # la vieja no cuenta
    response = await client.post(
        f"/exercise-instances/{instance_id}/tutor", json={}, headers=auth_headers
    )

    assert response.status_code == 429
    assert response.json() == {"code": "tutor_rate_limited"}


async def test_no_help_for_an_exercise_already_answered(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
) -> None:
    use_tutor_provider(None)
    started = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)
    instance_id = started.json()["current_exercise"]["instance_id"]
    answer = await answer_for(db, instance_id, correct=True)
    await client.post(
        f"/exercise-instances/{instance_id}/check", json={"answer": answer}, headers=auth_headers
    )

    response = await client.post(
        f"/exercise-instances/{instance_id}/tutor", json={}, headers=auth_headers
    )

    assert response.status_code == 409
    assert response.json() == {"code": "already_answered"}


async def test_other_users_instance_is_not_found(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    use_tutor_provider: UseProvider,
) -> None:
    use_tutor_provider(None)
    started = await client.post("/lessons/ohm-01/attempts", headers=auth_headers)
    instance_id = started.json()["current_exercise"]["instance_id"]
    other = await auth_service.register(
        db,
        email="otro@example.com",
        password="contraseña-segura",
        display_name="Otro",
        timezone="UTC",
    )

    response = await client.post(
        f"/exercise-instances/{instance_id}/tutor",
        json={},
        headers={"Authorization": f"Bearer {other.access_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"code": "not_found"}


async def test_requires_login_and_validates_the_message(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    url = "/exercise-instances/00000000-0000-0000-0000-000000000000/tutor"
    unauthenticated = await client.post(url, json={})
    too_long = await client.post(url, json={"message": "x" * 501}, headers=auth_headers)

    assert unauthenticated.status_code == 401
    assert too_long.status_code == 422
    assert too_long.json()["code"] == "validation_error"
