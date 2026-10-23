# syntax=docker/dockerfile:1

# --- СТАДИЯ 1: СБОРКА ФРОНТОВ (NODE, npm workspaces) ---
# Оба представления и общий пакет @pas/shared живут в одном воркспейсе,
# поэтому собираются одной стадией с одним npm ci.
FROM node:20-slim AS fe-builder
WORKDIR /app

# Сначала только манифесты — чтобы слой с зависимостями кэшировался
COPY representations/package.json representations/package-lock.json ./
COPY representations/shared/package.json ./shared/
COPY representations/web/package.json ./web/
COPY representations/tg_mini_app/package.json ./tg_mini_app/
RUN npm ci

COPY representations/ ./
RUN npm run build


# --- СТАДИЯ 2: СБОРКА (PYTHON) ---
FROM docker.io/python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.11 /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project \
    && /app/.venv/bin/python -c "import greenlet; from sqlalchemy.ext.asyncio import AsyncSession"


# --- СТАДИЯ 3: ВЫПОЛНЕНИЕ (RUNTIME) ---
FROM docker.io/python:3.14-slim AS runtime
WORKDIR /app
RUN mkdir -p /app/data

COPY --from=builder /app/.venv /app/.venv
COPY . .

COPY --from=fe-builder /app/tg_mini_app/dist /app/static/tg
COPY --from=fe-builder /app/web/dist /app/static/web
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app \
    PATH=/app/.venv/bin:$PATH

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "main"]

