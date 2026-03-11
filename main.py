import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from telegram.ext import (
    Application,
    CommandHandler,
    JobQueue,
    MessageHandler,
    filters,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.core.config import settings
from backend.core.db import init_db
from backend.tg_bot.handlers.add_account import add_account_conv
from backend.tg_bot.handlers.base import BaseHandler
from backend.tg_bot.handlers.list_accounts import list_accounts_conv
from backend.tg_bot.messages import BotMessages
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
FRONT_DIR = BASE_DIR / "frontend"


@app.get("/")
async def index():
    return FileResponse(FRONT_DIR / "index.html")


if __name__ == "__main__":
    asyncio.run(start())
