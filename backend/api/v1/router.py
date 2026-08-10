from fastapi import APIRouter

from backend.api.v1.account import router as account_router
from backend.api.v1.category import router as category_router
from backend.api.v1.custom_icon import router as custom_icon_router
from backend.api.v1.main_router import router as main_router
from backend.api.v1.resource import router as resource_router
from backend.api.v1.web_auth import router as web_auth_router

router = APIRouter(prefix="/v1")

router.include_router(main_router)
router.include_router(web_auth_router)
router.include_router(category_router)
router.include_router(custom_icon_router)
router.include_router(resource_router)
router.include_router(account_router)
