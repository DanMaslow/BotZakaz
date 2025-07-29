from sqlalchemy.future import select
from app.models.client import Client
from app.config import settings

async def get_client_by_telegram_id(session, telegram_id: int):
    result = await session.execute(select(Client).where(Client.telegram_id == telegram_id))
    return result.scalars().first()

async def create_client(session, telegram_id: int, name: str, phone_number: str):
    from app.config import ADMIN_ID

    is_admin = telegram_id == ADMIN_ID
    client = Client(
        telegram_id=telegram_id,
        name=name,
        phone_number=phone_number,
        admin=is_admin
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client

async def update_admin_flags(session):
    result = await session.execute(select(Client))
    clients = result.scalars().all()
    for client in clients:
        if client.telegram_id == ADMIN_ID and not client.admin:
            client.admin = True
    await session.commit()