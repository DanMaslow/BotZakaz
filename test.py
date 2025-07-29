import asyncio
from app.db.sesion import async_session
from app.crud.booking import get_free_slots

async def test():
    async with async_session() as session:
        slots = await get_free_slots(session)
        print(slots)

asyncio.run(test())