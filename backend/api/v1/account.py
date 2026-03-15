from fastapi import APIRouter, Depends, HTTPException

from backend.core.session import session_manager
from backend.dependencies import get_account_service, get_current_user
from backend.schemas.account import AccountRequestSchema, AccountListItemSchema, AccountDetailSchema
from backend.schemas.response_schemas import MessageResponse, SuccessResponse
from backend.services.account_service import AccountService

router = APIRouter(prefix="/account")


@router.get("/list/{platform_id}")
async def get_accounts_by_platform(
        platform_id: str,
        user: dict = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
) -> list[AccountListItemSchema]:
    """GET /pas-manager/v1/account/list/{platform_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    accounts = await service.get_accounts_by_platform(platform_id)
    return accounts


@router.get("/{account_id}")
async def get_account(
        account_id: int,
        user: dict = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
) -> AccountDetailSchema:
    """GET /pas-manager/v1/account/{account_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    master_password = session_manager.get_master_password(user["id"])
    if not master_password:
        raise HTTPException(status_code=401, detail="Master password not found")

    account = await service.get_account_decrypted(account_id, master_password)
    return account


@router.post("", response_model=AccountDetailSchema)
async def create_account(
        account: AccountRequestSchema,
        user: dict = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
):
    """POST /pas-manager/v1/account"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    master_password = session_manager.get_master_password(user["id"])
    if not master_password:
        raise HTTPException(status_code=401, detail="Master password not found")

    result = await service.create_account(account, master_password)
    return result


@router.put("/reorder", response_model=AccountDetailSchema)
async def reorder_accounts(
        payload: list[str],
        user: dict = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
):
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    await service.reorder_accounts(payload)
    return SuccessResponse()


@router.put("/{account_id}")
async def update_account(
        account_id: int,
        account: AccountRequestSchema,
        user: dict = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
):
    """PUT /pas-manager/v1/account/{account_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    master_password = session_manager.get_master_password(user["id"])
    if not master_password:
        raise HTTPException(status_code=401, detail="Master password not found")

    result = await service.update_account(account_id, account, master_password)
    return result


@router.delete("/{account_id}")
async def delete_account(
        account_id: int,
        user: dict = Depends(get_current_user),
        service: AccountService = Depends(get_account_service),
):
    """DELETE /pas-manager/v1/account/{account_id}"""
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    await service.delete_account(account_id)
    return MessageResponse(message='Account deleted')
