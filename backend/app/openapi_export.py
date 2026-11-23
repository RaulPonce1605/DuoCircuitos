"""Escribe el contrato OpenAPI en `backend/openapi.json`.

Uso (desde `backend/`): `uv run python -m app.openapi_export`

La app genera su cliente desde ese archivo (`npm run api:generate` en `app/`). El CI falla si el
archivo commiteado no coincide con el que produce el código, así que cualquier cambio de rutas o
schemas debe traer el `openapi.json` y el cliente regenerados en el mismo PR.
"""

import json
from pathlib import Path

from app.main import app

OUTPUT = Path(__file__).resolve().parents[1] / "openapi.json"


def render() -> str:
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> None:
    OUTPUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"OpenAPI escrito en {OUTPUT}")


if __name__ == "__main__":
    main()
