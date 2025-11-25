# --- СТАДИЯ 1: СБОРКА (BUILDER) ---
FROM python:3.11-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        python3-dev \
        libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y build-essential libsqlite3-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --all-extras --no-editable

# --- СТАДИЯ 2: ВЫПОЛНЕНИЕ (RUNTIME) ---

FROM python:3.11-slim as runtime

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /usr/local/lib/python3.11/site-packages

COPY . .

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app \
    UV_PYTHON_DOWNLOADS=never

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "app.main"]

