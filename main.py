import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.db import init_db
from backend.api.router import router

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down")


async def start() -> None:
    uvicorn_config = uvicorn.Config(
        app,
        host=settings.app.host,
        port=settings.app.port,
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


app = FastAPI(lifespan=lifespan)  # ← Добавь lifespan

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sde-resume.online",
        'https://bulkheaded-fleetly-alfreda.ngrok-free.dev',
        "https://web.telegram.org",
        "https://t.me",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
FRONT_DIR = BASE_DIR / "frontend"
STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("pas-manager/v1"):
            return {"detail": "Not Found", "ok": False}, 404

        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Frontend build not found"}
else:
    logger.warning(f"Static directory not found at {STATIC_DIR}")

if __name__ == "__main__":
    asyncio.run(start())
