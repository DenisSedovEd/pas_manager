#!/bin/bash
set -e

# Apply alembic migrations before starting app
uv run alembic upgrade head
python -m backend.utils.clear_bio_creds

# Run regular CMD (uvicorn)
exec "$@"