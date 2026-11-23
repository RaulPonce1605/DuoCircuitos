from typing import Annotated

from fastapi import APIRouter, Cookie, Response
from fastapi.responses import JSONResponse

from app.api.errors import VALIDATION_ERROR_RESPONSES, domain_error_response, error_responses
from app.core.config import get_settings
from app.core.db import DbSession
from app.schemas.auth import (
    AuthRead,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    SessionMode,
)
from app.schemas.common import StatusRead
from app.services import auth as auth_service
from app.services.errors import EmailTaken, InvalidCredentials, InvalidToken
from app.services.users import user_read

router = APIRouter(prefix="/auth", tags=["auth"], responses=VALIDATION_ERROR_RESPONSES)

REFRESH_COOKIE = "refresh_token"
REFRESH_COOKIE_PATH = "/auth"  # el navegador solo la manda a las rutas de auth
RefreshCookie = Annotated[str | None, Cookie(alias=REFRESH_COOKIE, include_in_schema=False)]


@router.post(
    "/register",
    response_model=AuthRead,
    status_code=201,
    operation_id="registerUser",
    responses=error_responses(EmailTaken),
)
async def register(body: RegisterRequest, db: DbSession, response: Response) -> AuthRead:
    session = await auth_service.register(
        db,
        email=body.email,
        password=body.password,
        display_name=body.display_name,
        timezone=body.timezone,
    )
    return _auth_response(session, body.session_mode, response)


@router.post(
    "/login",
    response_model=AuthRead,
    operation_id="loginUser",
    responses=error_responses(InvalidCredentials),
)
async def login(body: LoginRequest, db: DbSession, response: Response) -> AuthRead:
    session = await auth_service.login(db, email=body.email, password=body.password)
    return _auth_response(session, body.session_mode, response)


@router.post(
    "/refresh",
    response_model=AuthRead,
    operation_id="refreshSession",
    responses=error_responses(InvalidToken),
)
async def refresh(
    body: RefreshRequest, db: DbSession, response: Response, cookie_token: RefreshCookie = None
) -> AuthRead | JSONResponse:
    token = body.refresh_token if body.session_mode == "body" else cookie_token
    try:
        session = await auth_service.refresh(db, token)
    except InvalidToken as exc:
        # Se arma la respuesta aquí (y no en el manejador global) para poder borrar la cookie.
        error = domain_error_response(exc)
        if body.session_mode == "cookie":
            _clear_refresh_cookie(error)
        return error
    return _auth_response(session, body.session_mode, response)


@router.post("/logout", response_model=StatusRead, operation_id="logoutUser")
async def logout(
    body: LogoutRequest, db: DbSession, response: Response, cookie_token: RefreshCookie = None
) -> StatusRead:
    await auth_service.logout(db, body.refresh_token or cookie_token)
    _clear_refresh_cookie(response)
    return StatusRead(status="ok")


def _auth_response(
    session: auth_service.Session, mode: SessionMode, response: Response
) -> AuthRead:
    refresh_token: str | None = session.refresh_token
    if mode == "cookie":
        settings = get_settings()
        response.set_cookie(
            REFRESH_COOKIE,
            session.refresh_token,
            max_age=settings.jwt_refresh_ttl_days * 24 * 3600,
            path=REFRESH_COOKIE_PATH,
            httponly=True,
            secure=settings.refresh_cookie_secure,
            samesite=settings.refresh_cookie_samesite,
        )
        refresh_token = None
    return AuthRead(
        access_token=session.access_token,
        expires_in=session.expires_in,
        refresh_token=refresh_token,
        user=user_read(session.user),
    )


def _clear_refresh_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        REFRESH_COOKIE,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
    )
