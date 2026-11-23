import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient

REGISTER = {
    "email": "ana@example.com",
    "password": "contraseña-segura",
    "display_name": "Ana",
    "timezone": "America/Mexico_City",
}


async def _register(client: AsyncClient, **overrides: str) -> dict[str, object]:
    response = await client.post("/auth/register", json=REGISTER | overrides)
    assert response.status_code == 201, response.text
    data: dict[str, object] = response.json()
    return data


def _bearer(token: object) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Registro --------------------------------------------------------------------------------


async def test_register_returns_tokens_and_user(client: AsyncClient) -> None:
    data = await _register(client)

    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert isinstance(data["expires_in"], int) and data["expires_in"] > 0
    user = data["user"]
    assert isinstance(user, dict)
    assert user["email"] == "ana@example.com"
    assert user["timezone"] == "America/Mexico_City"
    assert "password_hash" not in user and "password" not in user


async def test_register_duplicate_email_is_409(client: AsyncClient) -> None:
    await _register(client)
    response = await client.post("/auth/register", json=REGISTER | {"email": "ANA@example.com"})

    assert response.status_code == 409
    assert response.json() == {"code": "email_taken"}


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "no-es-correo"},
        {"password": "corta"},
        {"password": "x" * 129},
        {"display_name": "   "},
        {"display_name": "x" * 51},
        {"timezone": "Marte/Olympus"},
        {"session_mode": "otro"},
    ],
)
async def test_register_validation_errors(client: AsyncClient, overrides: dict[str, str]) -> None:
    response = await client.post("/auth/register", json=REGISTER | overrides)

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


# --- Login -----------------------------------------------------------------------------------


async def test_login_ok(client: AsyncClient) -> None:
    await _register(client)
    response = await client.post(
        "/auth/login", json={"email": "ana@example.com", "password": "contraseña-segura"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["display_name"] == "Ana"


async def test_login_wrong_password_is_401(client: AsyncClient) -> None:
    await _register(client)
    response = await client.post(
        "/auth/login", json={"email": "ana@example.com", "password": "incorrecta"}
    )
    assert response.status_code == 401
    assert response.json() == {"code": "invalid_credentials"}


# --- /me y access token ----------------------------------------------------------------------


async def test_me_with_valid_token(client: AsyncClient) -> None:
    data = await _register(client)
    response = await client.get("/me", headers=_bearer(data["access_token"]))

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


async def test_me_without_token_is_401(client: AsyncClient) -> None:
    response = await client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"code": "invalid_token"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_me_rejects_tampered_tokens(client: AsyncClient) -> None:
    data = await _register(client)
    user_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    payload = {"sub": user_id, "type": "access", "iat": now, "exp": now + timedelta(minutes=5)}
    forged = jwt.encode(payload, "otro-secreto-que-no-es-el-del-servidor", algorithm="HS256")
    unsigned = jwt.encode(payload, None, algorithm="none")  # type: ignore[arg-type]

    for token in [forged, unsigned, data["refresh_token"], "basura"]:
        response = await client.get("/me", headers=_bearer(token))
        assert response.status_code == 401, token


# --- Refresh y logout (modo body: app móvil) -------------------------------------------------


async def test_refresh_body_mode_rotates(client: AsyncClient) -> None:
    data = await _register(client)
    response = await client.post("/auth/refresh", json={"refresh_token": data["refresh_token"]})

    assert response.status_code == 200
    assert response.json()["refresh_token"] != data["refresh_token"]
    reused = await client.post("/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert reused.status_code == 401
    assert reused.json() == {"code": "invalid_token"}


async def test_logout_body_mode(client: AsyncClient) -> None:
    data = await _register(client)
    response = await client.post("/auth/logout", json={"refresh_token": data["refresh_token"]})
    assert response.json() == {"status": "ok"}

    after = await client.post("/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert after.status_code == 401


# --- Modo cookie (app web) -------------------------------------------------------------------


async def test_cookie_mode_sets_httponly_cookie_and_hides_token(client: AsyncClient) -> None:
    response = await client.post("/auth/register", json=REGISTER | {"session_mode": "cookie"})

    assert response.status_code == 201
    assert response.json()["refresh_token"] is None
    set_cookie = response.headers["set-cookie"].lower()
    assert "refresh_token=" in set_cookie
    assert "httponly" in set_cookie
    assert "secure" in set_cookie
    assert "path=/auth" in set_cookie
    assert "samesite=lax" in set_cookie


async def test_cookie_mode_refresh_and_logout(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER | {"session_mode": "cookie"})

    refreshed = await client.post("/auth/refresh", json={"session_mode": "cookie"})
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] is None

    await client.post("/auth/logout", json={})
    assert "refresh_token" not in client.cookies
    after = await client.post("/auth/refresh", json={"session_mode": "cookie"})
    assert after.status_code == 401


async def test_cookie_mode_failed_refresh_clears_cookie(client: AsyncClient) -> None:
    client.cookies.set("refresh_token", "robado-o-viejo", domain="test", path="/auth")
    response = await client.post("/auth/refresh", json={"session_mode": "cookie"})

    assert response.status_code == 401
    assert response.json() == {"code": "invalid_token"}
    assert "refresh_token=" in response.headers["set-cookie"]
    assert "max-age=0" in response.headers["set-cookie"].lower()


async def test_body_mode_ignores_cookie(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER | {"session_mode": "cookie"})
    response = await client.post("/auth/refresh", json={"session_mode": "body"})
    assert response.status_code == 401
