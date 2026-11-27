from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    challenges,
    chests,
    health,
    leagues,
    lessons,
    path,
    shop,
    tutor,
    users,
)
from app.api.errors import register_error_handlers
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Circuitos API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,  # la app web manda la cookie del refresh token
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(path.router)
    app.include_router(lessons.router)
    app.include_router(tutor.router)
    app.include_router(chests.router)
    app.include_router(challenges.router)
    app.include_router(leagues.router)
    app.include_router(shop.router)
    return app


app = create_app()
