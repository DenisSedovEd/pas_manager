from fastapi import APIRouter, Depends, Header

from src.core.security import verify_telegram_data
from src.dependencies import get_account_service
from src.schemas.account import AccountRequestSchema
from src.services.account_service import AccountService
from src.schemas.account import AccountResponseSchema

router = APIRouter()


@router.get("/v1/account/list/{platform_id}")
async def get_accounts_by_platform(platform_id: int, authorization: str = Header(...)):
    verify_telegram_data(authorization)

    # Моковые данные в зависимости от платформы
    all_accounts = {
        1: [  # Google
            {"id": 101, "login": "user@gmail.com", "label": "Личный"},
            {"id": 102, "login": "work.dev@gmail.com", "label": "Рабочий"},
        ],
        2: [  # Telegram
            {"id": 201, "login": "@my_second_acc", "label": "Твинк"},
        ]
    }

    return all_accounts.get(platform_id, [{"id": 0, "login": "empty", "label": "Нет аккаунтов"}])
