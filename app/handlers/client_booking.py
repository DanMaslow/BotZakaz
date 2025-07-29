from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from app.db.sesion import async_session
from app.crud.slots import get_slots_by_date
from app.crud.client import get_client_by_telegram_id
from app.crud.booking import book_slot, get_bookings_by_client, cancel_booking
from app.models.booking import Booking

router = Router()

def generate_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    from calendar import monthrange
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    keyboard_rows = []

    # Строка с днями недели
    keyboard_rows.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in days])

    first_day = datetime(year, month, 1)
    start_day = first_day.weekday()  # Monday=0 ... Sunday=6
    if start_day == 6:
        start_day = -1

    empty_buttons = [InlineKeyboardButton(text=" ", callback_data="ignore")] * (start_day + 1)
    current_row = empty_buttons.copy()

    days_in_month = monthrange(year, month)[1]

    for day in range(1, days_in_month + 1):
        current_row.append(InlineKeyboardButton(text=str(day), callback_data=f"calendar_{year}_{month}_{day}"))
        if len(current_row) == 7:
            keyboard_rows.append(current_row)
            current_row = []

    if current_row:
        keyboard_rows.append(current_row)

    # Кнопки переключения месяцев
    keyboard_rows.append([
        InlineKeyboardButton(text="‹ Предыдущий", callback_data=f"calendar_prev_{year}_{month}"),
        InlineKeyboardButton(text="› Следующий", callback_data=f"calendar_next_{year}_{month}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


@router.message(lambda m: m.text == "📅 Записаться")
async def show_calendar(message: types.Message):
    now = datetime.now()
    calendar = generate_calendar(now.year, now.month)
    await message.answer("Выбери дату:", reply_markup=calendar)


@router.callback_query(lambda c: c.data and c.data.startswith("calendar_"))
async def calendar_handler(callback: CallbackQuery):
    data = callback.data.split("_")
    action = data[1]

    if action in ["prev", "next"]:
        year, month = int(data[2]), int(data[3])
        from calendar import monthrange
        if action == "prev":
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        else:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
        new_calendar = generate_calendar(year, month)
        await callback.message.edit_reply_markup(reply_markup=new_calendar)
        await callback.answer()
        return

    # Выбрали дату
    year, month, day = int(data[1]), int(data[2]), int(data[3])
    selected_date = datetime(year, month, day).date()

    async with async_session() as session:
        slots = await get_slots_by_date(session, selected_date)

    if not slots:
        await callback.message.answer(f"На дату {selected_date} слотов нет.")
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=slot.time.strftime('%H:%M'), callback_data=f"book_{slot.id}")]
        for slot in slots if not slot.is_booked
    ]
    if not buttons:
        await callback.message.answer(f"На дату {selected_date} все слоты заняты.")
        await callback.answer()
        return

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_calendar")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer(f"Свободные слоты на {selected_date}:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("book_"))
async def book_slot_callback(callback: CallbackQuery):
    slot_id = int(callback.data.split("_")[1])
    client_tg_id = callback.from_user.id

    async with async_session() as session:
        client = await get_client_by_telegram_id(session, client_tg_id)
        if not client:
            await callback.message.answer("Ты не зарегистрирован. Свяжись с админом.")
            await callback.answer()
            return

        success = await book_slot(session, client.id, slot_id)
        if success:
            await callback.message.answer("Ты записан на слот!")
        else:
            await callback.message.answer("Слот занят или не существует.")
        await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_calendar")
async def back_to_calendar(callback: CallbackQuery):
    now = datetime.now()
    calendar = generate_calendar(now.year, now.month)
    await callback.message.edit_text("Выбери дату:", reply_markup=calendar)
    await callback.answer()


@router.message(lambda m: m.text == "📋 Мои записи")
async def show_my_bookings(message: types.Message):
    client_tg_id = message.from_user.id
    async with async_session() as session:
        client = await get_client_by_telegram_id(session, client_tg_id)
        if not client:
            await message.answer("Ты не зарегистрирован. Свяжись с админом.")
            return

        bookings = await get_bookings_by_client(session, client.id)

        # Фильтрация только будущих записей
        bookings = [b for b in bookings if b.time_slot and b.time_slot.date >= datetime.now().date()]

        if not bookings:
            await message.answer("У тебя пока нет активных записей.")
            return

        text = "Твои активные записи:\n\n"
        buttons = []
        for b in bookings:
            date_str = b.time_slot.date.strftime("%Y-%m-%d")
            time_str = b.time_slot.time.strftime("%H:%M")
            text += f"— {date_str} {time_str}\n"
            buttons.append([
                InlineKeyboardButton(
                    text=f"❌ Отменить {date_str} {time_str}",
                    callback_data=f"cancel_{b.id}"
                )
            ])

        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("cancel_"))
async def cancel_booking_callback(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])
    client_tg_id = callback.from_user.id

    async with async_session() as session:
        client = await get_client_by_telegram_id(session, client_tg_id)
        if not client:
            await callback.message.answer("Ты не зарегистрирован.")
            await callback.answer()
            return

        booking = await session.get(Booking, booking_id)
        if booking and booking.time_slot:
            now = datetime.now()
            slot_dt = datetime.combine(booking.time_slot.date, booking.time_slot.time)
            if slot_dt - now < timedelta(hours=36):
                await callback.message.answer(
                    "Отмена записи менее чем за 36 часов невозможна. Свяжись с администратором."
                )
                await callback.answer()
                return

        success = await cancel_booking(session, client.id, booking_id)

        if success:
            await callback.message.answer("Запись отменена ✅")
        else:
            await callback.message.answer("Не удалось отменить запись ❌")

        # Показываем оставшиеся записи
        bookings = await get_bookings_by_client(session, client.id)
        bookings = [b for b in bookings if b.time_slot and b.time_slot.date >= datetime.now().date()]

        if not bookings:
            await callback.message.answer("У тебя больше нет активных записей.")
            await callback.answer()
            return

        text = "Оставшиеся записи:\n\n"
        buttons = []
        for b in bookings:
            date_str = b.time_slot.date.strftime("%Y-%m-%d")
            time_str = b.time_slot.time.strftime("%H:%M")
            text += f"— {date_str} {time_str}\n"
            buttons.append([
                InlineKeyboardButton(
                    text=f"❌ Отменить {date_str} {time_str}",
                    callback_data=f"cancel_{b.id}"
                )
            ])

        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer(text, reply_markup=keyboard)
        await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_menu")
async def go_back(callback: CallbackQuery):
    await callback.message.answer(
        "Возвращаюсь в меню 👇",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📅 Записаться")],
                [types.KeyboardButton(text="📋 Мои записи")],
            ],
            resize_keyboard=True
        )
    )
    await callback.answer()