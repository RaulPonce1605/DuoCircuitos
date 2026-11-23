# Se construye desde la RAÍZ del repo (docker-compose.yml: context: .) para incluir contenido/.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /srv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/ ./
# El importador busca el temario en ../contenido respecto a /srv → /contenido
COPY contenido/ /contenido/
RUN uv sync --frozen --no-dev

EXPOSE 8000
# Migraciones → temario → API
CMD ["sh", "-c", "uv run --no-dev alembic upgrade head && uv run --no-dev python -m app.content_import && exec uv run --no-dev fastapi run app/main.py --host 0.0.0.0 --port 8000"]
