from fastapi import APIRouter, Header

from src.core.security import verify_telegram_data

router = APIRouter(prefix="/platform")

@router.get('/platforms')
async def get_platforms(authorization: str = Header(...)):
    verify_telegram_data(authorization)

    return [
        {"id": 1, "name": "Google", "icon": "🌐", "accounts_count": 3},
        {"id": 2, "name": "Telegram", "icon": "✈️", "accounts_count": 1},
        {"id": 3, "name": "Work (GitHub)", "icon": "💻", "accounts_count": 2},
        {"id": 4, "name": "Banking", "icon": "💰", "accounts_count": 5},
        {"id": 5, "name": "Social", "icon": "📱", "accounts_count": 4},
    ]