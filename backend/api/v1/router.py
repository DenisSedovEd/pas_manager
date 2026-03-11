from fastapi import APIRouter

from backend.api.v1.main_router import router as main_router
from backend.api.v1.platform import router as platform_router
from backend.api.v1.account import router as account_router

router = APIRouter(prefix="/v1")

router.include_router(main_router)
router.include_router(platform_router)
router.include_router(account_router)