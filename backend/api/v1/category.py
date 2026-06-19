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
    """Корневые категории (parent_id IS NULL)"""
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.get_categories()


@router.get("/all")
async def get_all_categories(
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponseSchema]:
    """Все категории для выбора при перемещении аккаунта"""
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.get_all_categories()


@router.get("/{category_id}/children")
async def get_children(
    category_id: str,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponseSchema]:
    """Подкатегории для category_id"""
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.get_children(category_id)


@router.get("/{category_id}")
async def get_category(
    category_id: str,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponseSchema:
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.get_category(category_id)


@router.post("")
async def add_category(
    payload: CategoryRequestSchema,
    user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponseSchema:
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.add_category(payload)


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
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.update_category(category_id, payload)


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
