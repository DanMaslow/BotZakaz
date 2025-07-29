import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import view_slots

from app.config import settings
from app.handlers import client_booking, start, admin, admin_fsm  # твои роутеры

async def main():
    default_props = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=settings.BOT_TOKEN, default=default_props)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(client_booking.router)
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(admin_fsm.router)
    dp.include_router(view_slots.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())