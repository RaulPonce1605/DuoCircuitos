from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

from app.schemas.user import UserRead

# "body": el refresh token viaja en el JSON (app móvil, se guarda en expo-secure-store).
# "cookie": viaja en una cookie httpOnly que JavaScript no puede leer (app web).
SessionMode = Literal["body", "cookie"]

Password = Annotated[str, Field(min_length=8, max_length=128)]
DisplayName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


def _valid_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("zona horaria IANA inválida") from exc
    return value


Timezone = Annotated[str, Field(max_length=64), AfterValidator(_valid_timezone)]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: Password
    display_name: DisplayName
    timezone: Timezone = "UTC"
    session_mode: SessionMode = "body"


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=128)]
    session_mode: SessionMode = "body"


class RefreshRequest(BaseModel):
    """En modo cookie se omite `refresh_token`: el backend lo lee de la cookie."""

    refresh_token: str | None = None
    session_mode: SessionMode = "body"


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class AuthRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 - tipo de token, no un secreto
    expires_in: int
    # Solo en modo "body"; en modo "cookie" va en la cookie httpOnly y aquí es null.
    refresh_token: str | None
    user: UserRead
