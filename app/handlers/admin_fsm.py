from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import datetime

from app.db.sesion import async_session
from app.crud.slots import create_time_slot
from app.crud.booking import get_bookings_by_client

router = Router()

class AdminStates(StatesGroup):
    waiting_for_slots_count = State()
    waiting_for_slot_time = State()
    waiting_for_booking_date = State()

@router.message(AdminStates.waiting_for_slots_count)
async def process_slots_count(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Нужно ввести число. Попробуй ещё раз.")
        return

    count = int(message.text)
    if count < 1 or count > 24:
        await message.answer("Введи число от 1 до 24.")
        return

    await state.update_data(slots_count=count, times=[])
    await message.answer(f"Ок, всего слотов: {count}. Отправь время для слота 1 в формате ЧЧ:ММ")
    await state.set_state(AdminStates.waiting_for_slot_time)

@router.message(AdminStates.waiting_for_slot_time)
async def process_slot_time(message: Message, state: FSMContext):
    try:
        time_obj = datetime.datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        await message.answer("Неверный формат времени. Попробуй ЧЧ:ММ.")
        return

    data = await state.get_data()
    times = data.get("times", [])
    count = data.get("slots_count")

    times.append(time_obj)
    await state.update_data(times=times)

    if len(times) < count:
        await message.answer(f"Отлично! Отправь время для слота {len(times)+1} в формате ЧЧ:ММ")
    else:
        today = datetime.date.today()
        async with async_session() as session:
            for day_delta in range(14):
                slot_date = today + datetime.timedelta(days=day_delta)
                for t in times:
                    await create_time_slot(session, slot_date, t)

        await message.answer("Слоты успешно созданы на 14 дней!")
        await state.clear()

@router.message(AdminStates.waiting_for_booking_date)
async def process_booking_date(message: Message, state: FSMContext):
    try:
        date_obj = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Неверный формат даты. Попробуй ГГГГ-ММ-ДД")
        return

    async with async_session() as session:
        bookings = await get_bookings_by_client(session, None)  # Загружаем все брони, т.к. get_bookings_by_date нет

        # Фильтруем брони по дате вручную (все брони у Booking есть time_slot)
        bookings = [b for b in bookings if b.time_slot and b.time_slot.date == date_obj]

        if not bookings:
            await message.answer(f"На {date_obj} нет бронирований.")
        else:
            text = f"Бронирования на {date_obj}:\n"
            for b in bookings:
                client_name = b.client.name if b.client else "Неизвестный клиент"
                slot_time = b.time_slot.time.strftime("%H:%M") if b.time_slot else "неизвестно"
                text += f"— {client_name} в {slot_time}\n"
            await message.answer(text)

    await state.clear()