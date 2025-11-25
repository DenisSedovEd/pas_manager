FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential libsqlite3-dev && rm -rf /var/lib/apt/lists/*

#RUN pip install --no-cache-dir uv

#COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

#RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
#ENV PATH="/root/.local/bin/:$PATH"

ADD https://astral.sh/uv/0.9.11/install.sh /uv-installer.sh

WORKDIR /app

RUN uv sync --locked

COPY pyproject.toml uv.lock ./

COPY . .

ENV PYTHONPATH=/app \
    UV_PYTHON_DOWNLOADS=never

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "app.main"]