import asyncio

from backend.core.config import settings
from backend.core.db import async_session
from backend.models.app_settings import AppSettings
from backend.repositories import DatabaseRepository


async def clear_bio_creds():
    values = {
        'encrypted_master_password': None,
        'bio_enc_data': None,
    }
    filters = {
        'id': settings.app.admin_id
    }
    async with async_session() as session:
        repo = DatabaseRepository(session)
        await repo.update(AppSettings, filters=filters, values=values, )

    print("Biometric credentials cleared.")


if __name__ == '__main__':
    asyncio.run(clear_bio_creds())
