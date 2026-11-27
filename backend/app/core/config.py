from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, Field, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

BACKEND_DIR = Path(__file__).resolve().parents[2]


AchievementMetric = Literal[
    "lessons_completed",
    "streak_longest",
    "xp_total",
    "perfect_lessons",
    "units_completed",
    "chests_opened",
]


class AchievementDefinition(BaseModel):
    """Un logro con niveles: cada umbral alcanzado entrega una medalla
    (docs/diseno/cofres-y-logros.md). El nombre y la descripción viven en la app (i18n)."""

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    metric: AchievementMetric
    thresholds: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _thresholds_increase(self) -> Self:
        pairs = zip(self.thresholds, self.thresholds[1:], strict=False)
        if self.thresholds[0] <= 0 or any(a >= b for a, b in pairs):
            raise ValueError(f"los umbrales de {self.id} deben ser positivos y crecientes")
        return self


ChallengeKind = Literal[
    "earn_xp", "complete_lessons", "first_try_correct", "perfect_lessons", "open_chests"
]


class ChallengeTemplate(BaseModel):
    """Una meta posible para un desafío (docs/diseno/desafios.md). El texto vive en la app
    (i18n: `challenges.kind.<kind>`)."""

    kind: ChallengeKind
    goal: int = Field(gt=0)
    reward_xp: int = Field(ge=0)


DEFAULT_DAILY_CHALLENGES = [
    ChallengeTemplate(kind="earn_xp", goal=50, reward_xp=10),
    ChallengeTemplate(kind="complete_lessons", goal=2, reward_xp=10),
    ChallengeTemplate(kind="first_try_correct", goal=12, reward_xp=10),
    ChallengeTemplate(kind="perfect_lessons", goal=1, reward_xp=15),
    ChallengeTemplate(kind="open_chests", goal=2, reward_xp=5),
]
DEFAULT_MONTHLY_CHALLENGES = [ChallengeTemplate(kind="earn_xp", goal=1500, reward_xp=100)]


DEFAULT_ACHIEVEMENTS = [
    AchievementDefinition(id="lessons", metric="lessons_completed", thresholds=[1, 5, 10]),
    AchievementDefinition(id="streak", metric="streak_longest", thresholds=[3, 7, 30]),
    AchievementDefinition(id="xp", metric="xp_total", thresholds=[100, 500, 1500]),
    AchievementDefinition(id="perfect", metric="perfect_lessons", thresholds=[1, 5, 15]),
    AchievementDefinition(id="units", metric="units_completed", thresholds=[1, 3, 5]),
    AchievementDefinition(id="chests", metric="chests_opened", thresholds=[1, 10, 25]),
]


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
    # Energía (docs/diseno/energia.md): se gasta al fallar y se recarga una unidad cada N minutos.
    energy_max: int = Field(default=5, ge=1)
    energy_cost_per_mistake: int = Field(default=1, ge=0)
    energy_refill_minutes: int = Field(default=30, ge=1)
    # Nodos de repaso y evaluación (docs/diseno/repaso-y-evaluacion.md): cuántos ejercicios de la
    # unidad mezclan.
    review_exercise_count: int = Field(default=6, ge=1)
    assessment_exercise_count: int = Field(default=8, ge=1)
    # Cofres (docs/diseno/cofres-y-logros.md). El de lección sale al terminar cualquier nodo
    # jugable; el del camino es el nodo cofre.
    chest_lesson_xp_min: int = Field(default=2, ge=0)
    chest_lesson_xp_max: int = Field(default=10, ge=0)
    chest_lesson_energy: int = Field(default=1, ge=0)
    chest_node_xp_min: int = Field(default=15, ge=0)
    chest_node_xp_max: int = Field(default=30, ge=0)
    chest_node_energy: int = Field(default=5, ge=0)
    # Desafíos (docs/diseno/desafios.md): cada día se eligen DAILY_CHALLENGE_COUNT metas al azar
    # de la lista diaria; cada mes, todas las de la lista mensual.
    daily_challenge_count: int = Field(default=3, ge=1)
    daily_challenges: list[ChallengeTemplate] = Field(
        default_factory=lambda: list(DEFAULT_DAILY_CHALLENGES), min_length=1
    )
    monthly_challenges: list[ChallengeTemplate] = Field(
        default_factory=lambda: list(DEFAULT_MONTHLY_CHALLENGES)
    )
    # Logros y sus medallas. Se pueden cambiar con ACHIEVEMENTS (JSON).
    achievements: list[AchievementDefinition] = Field(
        default_factory=lambda: list(DEFAULT_ACHIEVEMENTS)
    )

    @model_validator(mode="after")
    def _rewards_are_consistent(self) -> Self:
        if self.chest_lesson_xp_min > self.chest_lesson_xp_max:
            raise ValueError("CHEST_LESSON_XP_MIN es mayor que CHEST_LESSON_XP_MAX")
        if self.chest_node_xp_min > self.chest_node_xp_max:
            raise ValueError("CHEST_NODE_XP_MIN es mayor que CHEST_NODE_XP_MAX")
        if len({a.id for a in self.achievements}) != len(self.achievements):
            raise ValueError("hay logros con el mismo id")
        for name, templates in [
            ("DAILY_CHALLENGES", self.daily_challenges),
            ("MONTHLY_CHALLENGES", self.monthly_challenges),
        ]:
            if len({t.kind for t in templates}) != len(templates):
                raise ValueError(f"{name} repite un tipo de desafío")
        return self

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
