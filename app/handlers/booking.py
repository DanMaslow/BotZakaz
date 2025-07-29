from aiogram import Router, F
from aiogram.types import Message
from app.db.database import async_session
from app.models.time_slot import TimeSlot
from app.models.booking import Booking
from sqlalchemy import select, update
from app.keyboards.user import free_slots_keyboard

router = Router()

@router.message(F.text == "📝 Записаться")
async def show_slots(message: Message):
    async with async_session() as session:
        res = await session.execute(
            select(TimeSlot).where(TimeSlot.is_booked == False).order_by(TimeSlot.date, TimeSlot.time)
        )
        free_slots = res.scalars().all()

    if not free_slots:
        await message.answer("На ближайшее время свободных слотов нет 😢")
        return

    await message.answer("Выбери слот:", reply_markup=free_slots_keyboard(free_slots))

@router.message(F.text.startswith("slot_"))
async def book_slot(message: Message):
    slot_id = int(message.text.split("_")[1])
    user_id = message.from_user.id

    async with async_session() as session:
        await session.execute(update(TimeSlot).where(TimeSlot.id == slot_id).values(is_booked=True))
        session.add(Booking(client_id=user_id, time_slot_id=slot_id))
        await session.commit()

    await message.answer(f"✅ Вы записаны на слот #{slot_id}")