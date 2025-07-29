import asyncio
from aiogram import Bot, Dispatcher
from app.config import settings
from app.handlers import registration

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(registration.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())