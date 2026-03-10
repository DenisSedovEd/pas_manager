from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from src.core.security import verify_telegram_data
from src.core.session import session_manager

router = APIRouter(prefix="/main")


class UnlockRequest(BaseModel):
    master_password: str


class BioUnlockRequest(BaseModel):
    bio_token: str


class StatusResponse(BaseModel):
    user_id: int
    is_unlocked: bool


class SuccessResponse(BaseModel):
    status: str
    ok: bool


