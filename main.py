import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.router import router
from backend.core.config import settings
from backend.core.db import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup application
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
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# add
app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
TG_STATIC_DIR = BASE_DIR / "static" / "tg"
WEB_STATIC_DIR = BASE_DIR / "static" / "web"

if TG_STATIC_DIR.exists():
    app.mount(
        "/tg/assets", StaticFiles(directory=TG_STATIC_DIR / "assets"), name="tg-assets"
    )

    @app.get("/tg/{full_path:path}")
    async def serve_tg_frontend(full_path: str):
        index_path = TG_STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "TG Mini App build not found"}

else:
    logger.warning(f"TG Mini App static directory not found at {TG_STATIC_DIR}")

if WEB_STATIC_DIR.exists():
    app.mount(
        "/assets", StaticFiles(directory=WEB_STATIC_DIR / "assets"), name="web-assets"
    )

    @app.get("/{full_path:path}")
    async def serve_web_frontend(full_path: str):
        index_path = WEB_STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Web SPA build not found"}

else:
    logger.warning(f"Web SPA static directory not found at {WEB_STATIC_DIR}")

if __name__ == "__main__":
    asyncio.run(start())
