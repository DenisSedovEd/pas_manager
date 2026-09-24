from fastapi import APIRouter, Depends, HTTPException

from backend.core.session import session_manager
from backend.dependencies import get_current_user, get_custom_field_service
from backend.schemas.custom_field_schema import (
    CustomFieldCreateSchema,
    CustomFieldDefinitionSchema,
    CustomFieldUpdateSchema,
    CustomFieldValueItemSchema,
    CustomFieldValuesReplaceSchema,
    EntityType,
)
from backend.schemas.response_schema import MessageResponse
from backend.services.custom_field_service import CustomFieldService

router = APIRouter(prefix="/custom-field")


def _require_active(user: dict) -> None:
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")


def _master_password(user: dict) -> str:
    password = session_manager.get_master_password(user["id"], user["session_kind"])
    if not password:
        raise HTTPException(status_code=401, detail="Master password not found")
    return password


@router.get("/list")
async def list_custom_fields(
    user: dict = Depends(get_current_user),
    service: CustomFieldService = Depends(get_custom_field_service),
) -> list[CustomFieldDefinitionSchema]:
    """Каталог определений кастомных полей."""
    _require_active(user)
    return await service.list_definitions()


@router.post("")
async def create_custom_field(
    data: CustomFieldCreateSchema,
    user: dict = Depends(get_current_user),
    service: CustomFieldService = Depends(get_custom_field_service),
) -> CustomFieldDefinitionSchema:
    """Создать определение поля."""
    _require_active(user)
    try:
        return await service.create_definition(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/values/{entity_type}/{entity_id}")
async def get_entity_custom_field_values(
    entity_type: EntityType,
    entity_id: str,
    user: dict = Depends(get_current_user),
    service: CustomFieldService = Depends(get_custom_field_service),
) -> list[CustomFieldValueItemSchema]:
    """Значения кастомных полей сущности (секреты расшифрованы)."""
    _require_active(user)
    master_password = _master_password(user)
    try:
        return await service.get_entity_values(
            entity_type,
            entity_id,
            master_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/values/{entity_type}/{entity_id}")
async def replace_entity_custom_field_values(
    entity_type: EntityType,
    entity_id: str,
    payload: CustomFieldValuesReplaceSchema,
    user: dict = Depends(get_current_user),
    service: CustomFieldService = Depends(get_custom_field_service),
) -> list[CustomFieldValueItemSchema]:
    """Атомарно заменить набор кастомных полей сущности."""
    _require_active(user)
    master_password = _master_password(user)
    try:
        return await service.replace_entity_values(
            entity_type,
            entity_id,
            payload,
            master_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{field_id}")
async def update_custom_field(
    field_id: str,
    data: CustomFieldUpdateSchema,
    user: dict = Depends(get_current_user),
    service: CustomFieldService = Depends(get_custom_field_service),
) -> CustomFieldDefinitionSchema:
    """Обновить определение (без смены is_secret)."""
    _require_active(user)
    try:
        return await service.update_definition(field_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{field_id}")
async def delete_custom_field(
    field_id: str,
    user: dict = Depends(get_current_user),
    service: CustomFieldService = Depends(get_custom_field_service),
) -> MessageResponse:
    """Удалить определение и все значения."""
    _require_active(user)
    try:
        await service.delete_definition(field_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MessageResponse(message="Custom field deleted")
