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

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_CACHE_DIR=/root/.cache/pip

RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import subprocess, tomllib; deps=tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']; subprocess.check_call(['pip', 'install', *deps])"


# --- СТАДИЯ 4: ВЫПОЛНЕНИЕ (RUNTIME) ---
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
    PATH=/app/.venv/bin:$PATH

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "main"]

