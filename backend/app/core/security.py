"""Hash de contraseñas (Argon2) y tokens (JWT de acceso + refresh opaco).

- El access token es un JWT HS256 de vida corta. Solo lleva el id del usuario (`sub`), nunca
  datos sensibles.
- El refresh token es un valor aleatorio opaco. En la base solo se guarda su SHA-256: con
  256 bits de entropía no hace falta un hash lento, y así se puede buscar por igualdad.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"  # noqa: S105 - es el tipo de token, no una contraseña

_password_hash = PasswordHash.recommended()
# Hash de una contraseña al azar: se verifica contra él cuando el correo no existe, para que el
# login tarde lo mismo exista o no la cuenta (no revela qué correos están registrados).
_DUMMY_HASH = _password_hash.hash(secrets.token_urlsafe(16))


class InvalidAccessToken(Exception):
    """El JWT no es válido, expiró o no es de acceso."""


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if password_hash is None:
        _password_hash.verify(password, _DUMMY_HASH)
        return False
    return _password_hash.verify(password, password_hash)


def create_access_token(user_id: uuid.UUID, now: datetime | None = None) -> tuple[str, int]:
    """Devuelve el token y sus segundos de vida."""
    settings = get_settings()
    issued_at = now or datetime.now(UTC)
    ttl = timedelta(minutes=settings.jwt_access_ttl_minutes)
    payload = {
        "sub": str(user_id),
        "type": ACCESS_TOKEN_TYPE,
        "iat": issued_at,
        "exp": issued_at + ttl,
        "jti": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=JWT_ALGORITHM)
    return token, int(ttl.total_seconds())


def decode_access_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            get_settings().jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat", "type"]},
        )
        if payload["type"] != ACCESS_TOKEN_TYPE:
            raise InvalidAccessToken
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError) as exc:
        raise InvalidAccessToken from exc


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
