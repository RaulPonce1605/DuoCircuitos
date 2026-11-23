from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.db import DbSession
from app.models import User
from app.services import auth as auth_service

# auto_error=False: la falta de token se reporta con nuestro código estable (invalid_token).
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    token = credentials.credentials if credentials else None
    return await auth_service.user_from_access_token(db, token)


CurrentUser = Annotated[User, Depends(get_current_user)]
