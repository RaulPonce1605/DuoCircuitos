from httpx import AsyncClient


async def test_me_includes_settings_with_defaults(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    me = (await client.get("/me", headers=auth_headers)).json()

    assert me["notify_streak_reminder"] is True
    assert me["notify_challenges"] is True
    assert me["profile_public"] is True


async def test_patch_changes_only_what_is_sent(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.patch(
        "/me",
        json={"display_name": "  Ana Luisa  ", "notify_challenges": False, "profile_public": False},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Ana Luisa"
    assert data["notify_challenges"] is False
    assert data["profile_public"] is False
    assert data["notify_streak_reminder"] is True  # no se mandó
    assert data["timezone"] == "America/Mexico_City"
    me = (await client.get("/me", headers=auth_headers)).json()
    assert me["display_name"] == "Ana Luisa"


async def test_patch_changes_the_timezone(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.patch("/me", json={"timezone": "Europe/Madrid"}, headers=auth_headers)
    assert response.json()["timezone"] == "Europe/Madrid"


async def test_patch_rejects_invalid_values(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    for body in [
        {"timezone": "Marte/Base"},
        {"display_name": "   "},
        {"display_name": "x" * 51},
        {"email": "otro@example.com"},  # el correo no se cambia aquí
    ]:
        response = await client.patch("/me", json=body, headers=auth_headers)
        assert response.status_code == 422, body
        assert response.json()["code"] == "validation_error"


async def test_patch_requires_login(client: AsyncClient) -> None:
    response = await client.patch("/me", json={"profile_public": False})
    assert response.status_code == 401
