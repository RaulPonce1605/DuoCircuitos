from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuración leída del entorno o de `backend/.env`. Es el único lugar que lee variables."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = "127.0.0.1"  # no "localhost": en Windows prueba IPv6 primero y es lento
    postgres_port: int = 5432
    # "disable" en local (asyncpg en Windows falla al negociar SSL con el Postgres de Docker);
    # "require" en un servidor real.
    postgres_ssl: Literal["disable", "prefer", "require"] = "disable"

    jwt_secret: SecretStr
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 30
    # Cookie del refresh token en la app web. En producción, si la app y la API están en dominios
    # distintos: REFRESH_COOKIE_SAMESITE=none (exige secure=true).
    refresh_cookie_secure: bool = True
    refresh_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    # Tutor (backend/CLAUDE.md 3.9). Sin proveedor, el tutor responde con las pistas del temario.
    llm_provider: Literal["", "anthropic"] = ""
    llm_model: str = ""
    llm_api_key: SecretStr = SecretStr("")
    # Esfuerzo de razonamiento del modelo; vacío = el predeterminado del modelo.
    llm_effort: Literal["", "low", "medium", "high"] = "low"
    llm_timeout_seconds: float = Field(default=30, gt=0)
    # Si el modelo rechaza la petición, el proveedor reintenta con otro modelo (Anthropic).
    llm_server_fallbacks: bool = True
    # Límites para no gastar de más: por usuario por hora y por ejercicio mostrado.
    tutor_requests_per_hour: int = Field(default=30, ge=1)
    tutor_requests_per_exercise: int = Field(default=6, ge=1)

    cors_origins: list[str] = []

    # Gamificación (docs/diseno/exp-y-racha.md). Nunca fijas en los servicios ni en la app.
    xp_per_exercise_first_try: int = Field(default=10, ge=0)
    xp_per_exercise_retry: int = Field(default=5, ge=0)
    xp_perfect_lesson_bonus: int = Field(default=5, ge=0)

    @model_validator(mode="after")
    def _llm_is_complete(self) -> Self:
        if self.llm_provider and not (self.llm_model and self.llm_api_key.get_secret_value()):
            raise ValueError("LLM_PROVIDER necesita LLM_MODEL y LLM_API_KEY")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        url = URL.create(
            "postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
            query={"ssl": self.postgres_ssl},
        )
        return url.render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
