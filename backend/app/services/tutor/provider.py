"""Interfaz de los proveedores de LLM del tutor (backend/CLAUDE.md 3.9).

Cada proveedor vive en su propio adaptador; el resto del backend solo conoce `TutorProvider`.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, Protocol


@dataclass(frozen=True)
class PromptMessage:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class TutorPrompt:
    """Lo que se le manda al LLM. Se arma SOLO con contenido del temario (prompt.py)."""

    system: str
    messages: tuple[PromptMessage, ...]

    def full_text(self) -> str:
        """Todo el texto del prompt junto (para las pruebas de que no se filtra la solución)."""
        return "\n".join([self.system, *(message.content for message in self.messages)])


class TutorProviderError(Exception):
    """El proveedor no respondió (red, límite, error del servicio, rechazo)."""


class TutorProvider(Protocol):
    async def complete(self, prompt: TutorPrompt) -> str:
        """Texto de la respuesta del modelo. Lanza `TutorProviderError` si no hay respuesta."""
        ...


@lru_cache
def get_tutor_provider() -> TutorProvider | None:
    """El proveedor configurado en `.env`, o None si no hay (el tutor da pistas del temario)."""
    from app.core.config import get_settings

    settings = get_settings()
    if settings.llm_provider == "anthropic":
        from app.services.tutor.anthropic_provider import AnthropicTutorProvider

        return AnthropicTutorProvider(
            model=settings.llm_model,
            api_key=settings.llm_api_key.get_secret_value(),
            effort=settings.llm_effort or None,
            timeout_seconds=settings.llm_timeout_seconds,
            server_fallbacks=settings.llm_server_fallbacks,
        )
    return None
