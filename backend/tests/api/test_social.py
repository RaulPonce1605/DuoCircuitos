from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import auth as auth_service


async def _register(db: AsyncSession, name: str, *, public: bool = True) -> auth_service.Session:
    session = await auth_service.register(
        db,
        email=f"{name.lower().replace(' ', '.')}@example.com",
        password="contraseña-segura",
        display_name=name,
        timezone="UTC",
    )
    session.user.profile_public = public
    await db.flush()
    return session


def _headers(session: auth_service.Session) -> dict[str, str]:
    return {"Authorization": f"Bearer {session.access_token}"}


async def test_search_finds_public_profiles_only(
    client: AsyncClient, db: AsyncSession, auth_headers: dict[str, str]
) -> None:
    await _register(db, "Luis Pérez")
    await _register(db, "Luisa Gómez", public=False)
    await _register(db, "Ana 50%")

    found = (await client.get("/users/search", params={"q": "LUIS"}, headers=auth_headers)).json()
    short = (await client.get("/users/search", params={"q": "l"}, headers=auth_headers)).json()
    literal = (await client.get("/users/search", params={"q": "0%"}, headers=auth_headers)).json()
    myself = (
        await client.get("/users/search", params={"q": "Alumna"}, headers=auth_headers)
    ).json()

    assert [card["display_name"] for card in found] == ["Luis Pérez"]
    assert short == []  # mínimo 2 letras
    assert [card["display_name"] for card in literal] == ["Ana 50%"]  # el % no es comodín
    assert myself == []  # uno mismo no sale


async def test_follow_unfollow_and_friends(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
) -> None:
    luis = await _register(db, "Luis")
    me_id = str(user_session.user.id)
    luis_id = str(luis.user.id)

    followed = await client.post(f"/users/{luis_id}/follow", headers=auth_headers)
    again = await client.post(f"/users/{luis_id}/follow", headers=auth_headers)  # no duplica
    back = await client.post(f"/users/{me_id}/follow", headers=_headers(luis))

    assert followed.status_code == 200
    assert followed.json()["is_following"] is True
    assert again.status_code == 200
    assert back.json() == {
        "id": me_id,
        "display_name": "Alumna",
        "xp_total": 0,
        "streak": 0,
        "league_tier": 0,
        "league_tier_id": "resistor",
        "is_following": True,
        "follows_me": True,  # ya son amigos
    }
    mine = (await client.get("/friends", headers=auth_headers)).json()
    assert [c["id"] for c in mine["following"]] == [luis_id]
    assert [c["id"] for c in mine["followers"]] == [luis_id]

    left = await client.delete(f"/users/{luis_id}/follow", headers=auth_headers)
    assert left.json()["is_following"] is False
    assert left.json()["follows_me"] is True
    mine = (await client.get("/friends", headers=auth_headers)).json()
    assert mine["following"] == []


async def test_follow_errors(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
) -> None:
    hidden = await _register(db, "Privada", public=False)

    itself = await client.post(f"/users/{user_session.user.id}/follow", headers=auth_headers)
    private = await client.post(f"/users/{hidden.user.id}/follow", headers=auth_headers)
    missing = await client.post(
        "/users/00000000-0000-0000-0000-000000000000/follow", headers=auth_headers
    )

    assert itself.json() == {"code": "cannot_follow_self"}
    assert private.status_code == 404
    assert missing.status_code == 404


async def test_a_private_follower_shows_without_name(
    client: AsyncClient,
    db: AsyncSession,
    auth_headers: dict[str, str],
    user_session: auth_service.Session,
) -> None:
    hidden = await _register(db, "Privada", public=False)
    await client.post(f"/users/{user_session.user.id}/follow", headers=_headers(hidden))

    mine = (await client.get("/friends", headers=auth_headers)).json()

    assert [(c["display_name"], c["follows_me"]) for c in mine["followers"]] == [(None, True)]


async def test_friends_require_login(client: AsyncClient) -> None:
    assert (await client.get("/friends")).status_code == 401
