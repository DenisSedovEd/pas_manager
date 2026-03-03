from fastapi import APIRouter
from src.api.v1.main_router import router as main_router

router = APIRouter(prefix="/pas-manager", tags=["v1"])

router.include_router(main_router)
