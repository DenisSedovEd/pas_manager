from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.core.session import session_manager
from backend.dependencies import get_current_user, get_custom_icon_service
from backend.schemas.custom_icon import CustomIconResponseSchema
from backend.schemas.response_schema import MessageResponse
from backend.services.custom_icon_service import CustomIconService

router = APIRouter(prefix="/custom-icon")


@router.get("/list")
async def list_custom_icons(
    user: dict = Depends(get_current_user),
    service: CustomIconService = Depends(get_custom_icon_service),
) -> list[CustomIconResponseSchema]:
    """Список пользовательских иконок."""
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.list_icons()


@router.post("")
async def upload_custom_icon(
    file: UploadFile = File(...),
    label: str | None = Form(default=None),
    fallback_emoji: str = Form(default="📁"),
    user: dict = Depends(get_current_user),
    service: CustomIconService = Depends(get_custom_icon_service),
) -> CustomIconResponseSchema:
    """Загрузить PNG/JPEG/WebP/SVG иконку."""
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    content_type = file.content_type or ""
    data = await file.read()
    try:
        return await service.create_icon(
            data=data,
            content_type=content_type,
            label=label,
            fallback_emoji=fallback_emoji,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{icon_id}/file")
async def get_custom_icon_file(
    icon_id: str,
    user: dict = Depends(get_current_user),
    service: CustomIconService = Depends(get_custom_icon_service),
) -> FileResponse:
    """Отдать файл иконки."""
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    try:
        path, content_type = await service.get_file(icon_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type=content_type)


@router.delete("/{icon_id}")
async def delete_custom_icon(
    icon_id: str,
    user: dict = Depends(get_current_user),
    service: CustomIconService = Depends(get_custom_icon_service),
) -> MessageResponse:
    """Удалить иконку; категории с ней получают fallback."""
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    try:
        await service.delete_icon(icon_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MessageResponse(message="Custom icon deleted")
