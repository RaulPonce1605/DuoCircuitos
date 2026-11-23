"""Infraestructura de pruebas sobre PostgreSQL real (backend/CLAUDE.md 3.12).

- La base de pruebas es `<POSTGRES_DB>_test` en el mismo servidor; se crea si no existe y sus
  tablas se recrean al inicio de cada corrida con `create_all` (permitido solo en pruebas).
- Cada prueba corre dentro de una transacción que se deshace al terminar, así que las pruebas no
  se ven entre sí aunque hagan commit (se usan savepoints).
- Sin `backend/.env` (por ejemplo en el CI) las credenciales salen de variables de entorno.
"""

import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine

if not (Path(__file__).resolve().parents[1] / ".env").exists():
    os.environ.setdefault("POSTGRES_USER", "circuitos")
    os.environ.setdefault("POSTGRES_PASSWORD", "circuitos")
    os.environ.setdefault("POSTGRES_DB", "circuitos")
    os.environ.setdefault("JWT_SECRET", "solo-para-pruebas")

from app.core.config import get_settings
from app.core.db import get_db
from app.main import app
from app.models import Base
from app.services import auth as auth_service


def _test_database_url() -> str:
    url = make_url(get_settings().database_url)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


async def _ensure_database_exists(database_url: str) -> None:
    url = make_url(database_url)
    admin = create_async_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        async with admin.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    finally:
        await admin.dispose()


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    database_url = _test_database_url()
    await _ensure_database_exists(database_url)
    test_engine = create_async_engine(database_url)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def connection(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with engine.connect() as conn:
        transaction = await conn.begin()
        yield conn
        await transaction.rollback()


@pytest.fixture
async def db(connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    session = AsyncSession(
        bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
    )
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
async def client(db: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP contra la app, usando la misma sesión (y transacción) que la prueba."""

    async def _get_db() -> AsyncIterator[AsyncSession]:
        yield db

    app.dependency_overrides[get_db] = _get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)


# --- Datos comunes ---------------------------------------------------------------------------


@pytest.fixture
async def syllabus(db: AsyncSession) -> None:
    """Importa el temario real en la base de pruebas (dentro de la transacción de la prueba)."""
    from app.content_import.importer import import_syllabus
    from app.content_import.validate import DEFAULT_SYLLABUS_DIR

    await import_syllabus(db, DEFAULT_SYLLABUS_DIR)


@pytest.fixture
async def user_session(db: AsyncSession) -> "auth_service.Session":
    return await auth_service.register(
        db,
        email="alumna@example.com",
        password="contraseña-segura",
        display_name="Alumna",
        timezone="America/Mexico_City",
    )


@pytest.fixture
def auth_headers(user_session: "auth_service.Session") -> dict[str, str]:
    return {"Authorization": f"Bearer {user_session.access_token}"}
