from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.db.database import async_session
from app.models.client import Client
from sqlalchemy import select

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📝 Записаться"), KeyboardButton(text="❌ Отменить запись")],
    ], resize_keyboard=True)
    await message.answer("Привет! Я бот для записи на ресницы 💅", reply_markup=kb)

    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.telegram_id == message.from_user.id))
        client = result.scalar_one_or_none()
        if not client:
            session.add(Client(
                telegram_id=message.from_user.id,
                name=message.from_user.full_name
            ))
            await session.commit()