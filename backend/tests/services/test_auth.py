from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_refresh_token
from app.models import RefreshToken, User
from app.services import auth
from app.services.errors import EmailTaken, InvalidCredentials, InvalidToken


async def _register(db: AsyncSession, email: str = "Ana@Example.com") -> auth.Session:
    return await auth.register(
        db, email=email, password="contraseña-segura", display_name="Ana", timezone="UTC"
    )


async def test_register_normalizes_email_and_hashes_password(db: AsyncSession) -> None:
    session = await _register(db)

    user = await db.scalar(select(User))
    assert user is not None
    assert user.email == "ana@example.com"
    assert user.password_hash.startswith("$argon2id$")
    assert "contraseña-segura" not in user.password_hash
    assert session.user.id == user.id


async def test_register_stores_only_refresh_token_hash(db: AsyncSession) -> None:
    session = await _register(db)

    stored = await db.scalar(select(RefreshToken))
    assert stored is not None
    assert stored.token_hash == hash_refresh_token(session.refresh_token)
    assert session.refresh_token not in stored.token_hash


async def test_register_rejects_duplicate_email_case_insensitive(db: AsyncSession) -> None:
    await _register(db, "ana@example.com")
    with pytest.raises(EmailTaken):
        await _register(db, "  ANA@example.com ")


async def test_login_ok(db: AsyncSession) -> None:
    await _register(db)
    session = await auth.login(db, email="ANA@example.com", password="contraseña-segura")
    assert session.user.email == "ana@example.com"


@pytest.mark.parametrize(
    ("email", "password"),
    [("ana@example.com", "incorrecta"), ("nadie@example.com", "contraseña-segura")],
)
async def test_login_errors_do_not_reveal_which_part_failed(
    db: AsyncSession, email: str, password: str
) -> None:
    await _register(db)
    with pytest.raises(InvalidCredentials):
        await auth.login(db, email=email, password=password)


async def test_refresh_rotates_token(db: AsyncSession) -> None:
    first = await _register(db)
    second = await auth.refresh(db, first.refresh_token)

    assert second.refresh_token != first.refresh_token
    old = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(first.refresh_token)
        )
    )
    assert old is not None and old.revoked_at is not None


async def test_reusing_rotated_token_revokes_whole_family(db: AsyncSession) -> None:
    first = await _register(db)
    second = await auth.refresh(db, first.refresh_token)

    with pytest.raises(InvalidToken):
        await auth.refresh(db, first.refresh_token)  # reutilización: posible robo
    with pytest.raises(InvalidToken):
        await auth.refresh(db, second.refresh_token)  # la familia quedó revocada


async def test_other_logins_survive_family_revocation(db: AsyncSession) -> None:
    phone = await _register(db)
    laptop = await auth.login(db, email="ana@example.com", password="contraseña-segura")
    await auth.logout(db, phone.refresh_token)

    assert (await auth.refresh(db, laptop.refresh_token)).user.email == "ana@example.com"


async def test_expired_refresh_token_is_rejected(db: AsyncSession) -> None:
    session = await _register(db)
    stored = await db.scalar(select(RefreshToken))
    assert stored is not None
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db.flush()

    with pytest.raises(InvalidToken):
        await auth.refresh(db, session.refresh_token)


@pytest.mark.parametrize("token", [None, "", "no-existe"])
async def test_refresh_with_missing_or_unknown_token(db: AsyncSession, token: str | None) -> None:
    with pytest.raises(InvalidToken):
        await auth.refresh(db, token)


async def test_logout_revokes_and_is_idempotent(db: AsyncSession) -> None:
    session = await _register(db)
    await auth.logout(db, session.refresh_token)
    await auth.logout(db, session.refresh_token)
    await auth.logout(db, "desconocido")
    await auth.logout(db, None)

    with pytest.raises(InvalidToken):
        await auth.refresh(db, session.refresh_token)


async def test_user_from_access_token(db: AsyncSession) -> None:
    session = await _register(db)
    user = await auth.user_from_access_token(db, session.access_token)
    assert user.id == session.user.id


async def test_expired_access_token_is_rejected(db: AsyncSession) -> None:
    session = await _register(db)
    token, _ = create_access_token(session.user.id, now=datetime.now(UTC) - timedelta(hours=1))
    with pytest.raises(InvalidToken):
        await auth.user_from_access_token(db, token)


@pytest.mark.parametrize("token", [None, "", "basura", "a.b.c"])
async def test_garbage_access_token_is_rejected(db: AsyncSession, token: str | None) -> None:
    with pytest.raises(InvalidToken):
        await auth.user_from_access_token(db, token)
