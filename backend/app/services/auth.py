"""Registro, inicio de sesión y rotación de refresh tokens (backend/CLAUDE.md 3.6)."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    InvalidAccessToken,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models import User
from app.models.auth import RefreshToken
from app.services.errors import EmailTaken, InvalidCredentials, InvalidToken


@dataclass(frozen=True)
class Session:
    user: User
    access_token: str
    expires_in: int
    refresh_token: str


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def register(
    db: AsyncSession, *, email: str, password: str, display_name: str, timezone: str
) -> Session:
    email = normalize_email(email)
    if await db.scalar(select(User.id).where(User.email == email)) is not None:
        raise EmailTaken
    user = User(
        email=email,
        display_name=display_name,
        password_hash=hash_password(password),
        timezone=timezone,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as exc:  # dos registros simultáneos con el mismo correo
        await db.rollback()
        raise EmailTaken from exc
    session = await _start_session(db, user, family_id=uuid.uuid4())
    await db.commit()
    return session


async def login(db: AsyncSession, *, email: str, password: str) -> Session:
    user = await db.scalar(select(User).where(User.email == normalize_email(email)))
    if not verify_password(password, user.password_hash if user else None) or user is None:
        raise InvalidCredentials
    session = await _start_session(db, user, family_id=uuid.uuid4())
    await db.commit()
    return session


async def refresh(db: AsyncSession, refresh_token: str | None) -> Session:
    """Cambia un refresh token válido por uno nuevo (y un access token nuevo)."""
    if not refresh_token:
        raise InvalidToken
    now = datetime.now(UTC)
    stored = await db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(refresh_token))
        .with_for_update()
    )
    if stored is None:
        raise InvalidToken
    if stored.revoked_at is not None:
        # Reutilizar un token ya rotado indica que alguien más lo tiene: se corta toda la familia.
        await _revoke_family(db, stored.family_id, now)
        await db.commit()
        raise InvalidToken
    if stored.expires_at <= now:
        raise InvalidToken

    stored.revoked_at = now
    user = await db.get(User, stored.user_id)
    if user is None:  # pragma: no cover - el borrado de usuarios revoca en cascada
        raise InvalidToken
    session = await _start_session(db, user, family_id=stored.family_id, now=now)
    await db.commit()
    return session


async def logout(db: AsyncSession, refresh_token: str | None) -> None:
    """Revoca la sesión de ese refresh token. Es idempotente: un token desconocido no es error."""
    if not refresh_token:
        return
    stored = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(refresh_token))
    )
    if stored is not None:
        await _revoke_family(db, stored.family_id, datetime.now(UTC))
        await db.commit()


async def user_from_access_token(db: AsyncSession, token: str | None) -> User:
    if not token:
        raise InvalidToken
    try:
        user_id = decode_access_token(token)
    except InvalidAccessToken as exc:
        raise InvalidToken from exc
    user = await db.get(User, user_id)
    if user is None:
        raise InvalidToken
    return user


async def _start_session(
    db: AsyncSession, user: User, *, family_id: uuid.UUID, now: datetime | None = None
) -> Session:
    now = now or datetime.now(UTC)
    refresh_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            family_id=family_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=now + timedelta(days=get_settings().jwt_refresh_ttl_days),
        )
    )
    await db.flush()
    access_token, expires_in = create_access_token(user.id, now=now)
    return Session(user, access_token, expires_in, refresh_token)


async def _revoke_family(db: AsyncSession, family_id: uuid.UUID, now: datetime) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
