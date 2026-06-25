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


# --- СТАДИЯ 2: СБОРКА (PYTHON) ---
FROM docker.io/python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras --no-editable


# --- СТАДИЯ 3: ВЫПОЛНЕНИЕ (RUNTIME) ---
FROM docker.io/python:3.14-slim AS runtime
WORKDIR /app
RUN mkdir -p /app/data

#COPY --from=builder /src/.venv/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /app/.venv /app/.venv
COPY . .

COPY --from=tg-builder /app/dist /app/static/tg
COPY --from=web-builder /app/dist /app/static/web
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app \
    UV_PYTHON_DOWNLOADS=never \
    PATH=/app/.venv/bin:$PATH

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "main"]

