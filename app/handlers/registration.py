from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states.registration import RegStates
from app.models.client import Client
from app.db.database import  async_session
from sqlalchemy import select
import re

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(
            select(Client).where(Client.telegram_id == message.from_user.id)
        )
        client = result.scalar_one_or_none()

        if client:
            await message.answer("👋 Ты уже зарегистрирован!")
            return

    await message.answer("👋 Как тебя зовут?")
    await state.set_state(RegStates.name)

@router.message(RegStates.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введи свой номер телефона в формате +7XXXXXXXXXX")
    await state.set_state(RegStates.phone)

@router.message(RegStates.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not re.fullmatch(r"\+7\d{10}", phone):
        await message.answer("❌ Неверный формат. Попробуй ещё раз.")
        return

    data = await state.get_data()

    async with async_session() as session:
        client = Client(
            telegram_id=message.from_user.id,
            name=data["name"],
            phone_number=phone
        )
        session.add(client)
        await session.commit()

    await state.clear()
    await message.answer("✅ Ты успешно зарегистрирован!")