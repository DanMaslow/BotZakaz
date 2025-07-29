from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select, and_
from datetime import datetime
from app.db.sesion import async_session
from app.models.time_slot import TimeSlot
from app.crud.client import get_client_by_telegram_id
from app.crud.booking import book_slot

router = Router()

# Показываем 10 ближайших свободных слотов
@router.message(lambda msg: msg.text == "📅 Свободные слоты")
async def view_slots(message: Message):
    now = datetime.now()
    async with async_session() as session:
        stmt = (
            select(TimeSlot)
            .where(
                and_(
                    TimeSlot.is_booked == False,
                    TimeSlot.date >= now.date()
                )
            )
            .order_by(TimeSlot.date, TimeSlot.time)
            .limit(10)
        )
        result = await session.execute(stmt)
        slots = result.scalars().all()

    if not slots:
        await message.answer("Нет доступных слотов 😢")
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"{slot.date.strftime('%d.%m')} в {slot.time.strftime('%H:%M')}",
            callback_data=f"slot_{slot.id}"
        )]
        for slot in slots
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Свободные слоты:", reply_markup=keyboard)

# Хендлер для записи на слот при нажатии на кнопку
@router.callback_query(lambda c: c.data and c.data.startswith("slot_"))
async def slot_booking_callback(callback: CallbackQuery):
    slot_id = int(callback.data.split("_")[1])
    client_tg_id = callback.from_user.id

    async with async_session() as session:
        client = await get_client_by_telegram_id(session, client_tg_id)
        if not client:
            await callback.message.answer("Ты не зарегистрирован. Свяжись с админом.")
            await callback.answer()
            return

        slot = await session.get(TimeSlot, slot_id)
        if not slot or slot.is_booked:
            await callback.message.answer("Слот уже занят или не найден.")
            await callback.answer()
            return

        success = await book_slot(session, client.id, slot_id)
        if success:
            await callback.message.answer(
                f"✅ Ты записан на {slot.date.strftime('%d.%m')} в {slot.time.strftime('%H:%M')}")
        else:
            await callback.message.answer("❌ Не удалось записаться на этот слот.")
        await callback.answer()