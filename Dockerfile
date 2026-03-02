# --- СТАДИЯ 1: СБОРКА (BUILDER) ---
FROM docker.io/python:3.13-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y build-essential libsqlite3-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --all-extras --no-editable

# --- СТАДИЯ 2: ВЫПОЛНЕНИЕ (RUNTIME) ---

FROM docker.io/python:3.13-slim AS runtime

WORKDIR /app

RUN pip install --no-cache-dir uv

RUN mkdir -p /app/data

#COPY --from=builder /src/.venv/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app/.venv /app/.venv
COPY . .

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app \
    UV_PYTHON_DOWNLOADS=never \
    PATH=/app/.venv/bin:$PATH

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "src.main"]

