from fastapi import APIRouter, Depends, HTTPException

from backend.core.session import session_manager
from backend.dependencies import get_category_service, get_current_user
from backend.schemas.category import CategoryResponseSchema, CategoryRequestSchema
from backend.schemas.response_schema import MessageResponse, SuccessResponse
from backend.services.category_service import CategoryService

router = APIRouter(prefix="/category")


@router.get("/list")
async def get_categories(
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponseSchema]:
    """GET /pas-manager/v1/category/list"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    categories = await service.get_categories()
    return categories


@router.get("/{category_id}")
async def get_category(
    category_id: str,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponseSchema:
    """GET /pas-manager/v1/category/{category_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    category = await service.get_category(category_id)
    return category


@router.post("")
async def add_category(
    payload: CategoryRequestSchema,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponseSchema:
    """POST /pas-manager/v1/category"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    new_category = await service.add_category(payload)
    return new_category


@router.put("/reorder")
async def reorder_categories(
    payload: list[str],
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    await service.reorder_categories(payload)
    return SuccessResponse()


@router.put("/{category_id}")
async def update_category(
    category_id: str,
    payload: CategoryRequestSchema,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponseSchema:
    """PUT /pas-manager/v1/category/{category_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    category = await service.update_category(category_id, payload)
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    transfer: bool = True,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    try:
        await service.delete_category(category_id, transfer_accounts=transfer)
        return MessageResponse(message="Category deleted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
