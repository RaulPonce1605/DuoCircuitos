"""Adaptador de Claude (Anthropic) para el tutor. Es el ÚNICO archivo que usa el SDK."""

from typing import Any

import anthropic
from anthropic.types.beta import (
    BetaAssistantMessageParam,
    BetaMessageParam,
    BetaUserMessageParam,
)

from app.services.tutor.provider import PromptMessage, TutorPrompt, TutorProviderError

# Las pistas son cortas, pero el modelo también razona antes de responder.
_MAX_TOKENS = 4096
_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicTutorProvider:
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        effort: str | None,
        timeout_seconds: float,
        server_fallbacks: bool,
    ) -> None:
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key, timeout=timeout_seconds, max_retries=1
        )
        self._model = model
        self._effort = effort
        self._server_fallbacks = server_fallbacks

    async def complete(self, prompt: TutorPrompt) -> str:
        options: dict[str, Any] = {}
        if self._effort:
            options["output_config"] = {"effort": self._effort}
        if self._server_fallbacks:
            # Si el modelo rechaza la petición, la API la repite con otro modelo adecuado.
            options["betas"] = [_FALLBACK_BETA]
            options["fallbacks"] = "default"
        try:
            response = await self._client.beta.messages.create(
                model=self._model,
                max_tokens=_MAX_TOKENS,
                system=prompt.system,
                messages=[_message_param(message) for message in prompt.messages],
                **options,
            )
        except anthropic.APIConnectionError as exc:
            raise TutorProviderError("sin conexión con el proveedor") from exc
        except anthropic.APIStatusError as exc:
            raise TutorProviderError(f"el proveedor respondió {exc.status_code}") from exc
        if response.stop_reason == "refusal":
            raise TutorProviderError("el modelo rechazó la petición")
        text = "".join(block.text for block in response.content if block.type == "text")
        if not text.strip():
            raise TutorProviderError("respuesta vacía")
        return text


def _message_param(message: PromptMessage) -> BetaMessageParam:
    if message.role == "user":
        return BetaUserMessageParam(role="user", content=message.content)
    return BetaAssistantMessageParam(role="assistant", content=message.content)
