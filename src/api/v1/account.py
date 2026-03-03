from fastapi import APIRouter, Depends

from src.dependencies import get_account_service
from src.schemas.account import AccountRequestSchema
from src.services.account_service import AccountService
from src.schemas.account import AccountResponseSchema

router = APIRouter()


@router.post("/account", response_model=AccountResponseSchema)
async def create_account(
    request: AccountRequestSchema,
    service: AccountService = Depends(get_account_service),
):
    return service.create_account(request)
    pass
