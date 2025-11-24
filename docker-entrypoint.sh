#!/bin/bash
set -e

# Apply alembic migrations before starting app
uv run alembic upgrade head

# Run regular CMD (uvicorn)
exec "$@"