from typing import Literal

from pydantic import BaseModel, Field


class TutorRequest(BaseModel):
    # Opcional: el alumno puede pulsar "Pedir ayuda" sin escribir nada.
    message: str | None = Field(default=None, max_length=500)


class TutorReplyRead(BaseModel):
    reply: str
    # "llm": la escribió el tutor y pasó el filtro. "hint": pista del temario (sin proveedor,
    # si el proveedor falló o si el filtro bloqueó la respuesta del modelo).
    source: Literal["llm", "hint"]
    # Cuántas veces se ha pedido ayuda en este ejercicio, contando esta.
    help_level: int
    # Cuántas veces más se puede pedir ayuda ahora (el menor de los dos límites).
    remaining_requests: int
