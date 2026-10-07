# syntax=docker/dockerfile:1

# --- СТАДИЯ 1: СБОРКА TG MINI APP (NODE) ---
FROM node:20-slim AS tg-builder
WORKDIR /app
COPY representations/tg_mini_app/package*.json ./
RUN npm install
COPY representations/tg_mini_app/ ./
RUN npm run build


# --- СТАДИЯ 2: СБОРКА WEB SPA (NODE) ---
FROM node:20-slim AS web-builder
WORKDIR /app
COPY representations/web/package*.json ./
RUN npm install
COPY representations/web/ ./
RUN npm run build


# --- СТАДИЯ 3: СБОРКА (PYTHON) ---
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


# --- СТАДИЯ 4: ВЫПОЛНЕНИЕ (RUNTIME) ---
FROM docker.io/python:3.14-slim AS runtime
WORKDIR /app
RUN mkdir -p /app/data

COPY --from=builder /app/.venv /app/.venv
COPY . .

COPY --from=tg-builder /app/dist /app/static/tg
COPY --from=web-builder /app/dist /app/static/web
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app \
    PATH=/app/.venv/bin:$PATH

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "main"]

