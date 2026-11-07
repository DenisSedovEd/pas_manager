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
from backend.core.http_security import add_security_headers

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
        # За cloudflared/реверс-прокси без этого все запросы выглядят как
        # http с одного IP: rate limit считает всех одним клиентом, а cookie
        # не получает Secure. None — поведение uvicorn по умолчанию.
        **(
            {"forwarded_allow_ips": settings.app.forwarded_allow_ips}
            if settings.app.forwarded_allow_ips
            else {}
        ),
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


# /docs и /openapi.json — полная карта API менеджера паролей, и авторизация их
# не закрывает. Вне debug выключаем.
_expose_docs = (
    settings.app.expose_docs
    if settings.app.expose_docs is not None
    else settings.app.debug
)

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if _expose_docs else None,
    redoc_url="/redoc" if _expose_docs else None,
    openapi_url="/openapi.json" if _expose_docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
add_security_headers(app)
# add
app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
TG_STATIC_DIR = BASE_DIR / "static" / "tg"
WEB_STATIC_DIR = BASE_DIR / "static" / "web"

if TG_STATIC_DIR.exists():
    app.mount(
        "/tg/assets", StaticFiles(directory=TG_STATIC_DIR / "assets"), name="tg-assets"
    )

    @app.get("/tg")
    async def serve_tg_root():
        index_path = TG_STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "TG Mini App build not found"}

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
        "/web/assets",
        StaticFiles(directory=WEB_STATIC_DIR / "assets"),
        name="web-assets",
    )

    @app.get("/web")
    async def serve_web_root():
        index_path = WEB_STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Web SPA build not found"}

    @app.get("/web/{full_path:path}")
    async def serve_web_frontend(full_path: str):
        index_path = WEB_STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Web SPA build not found"}

    @app.get("/")
    async def redirect_to_web():
        return FileResponse(WEB_STATIC_DIR / "index.html")

else:
    logger.warning(f"Web SPA static directory not found at {WEB_STATIC_DIR}")

if __name__ == "__main__":
    asyncio.run(start())
