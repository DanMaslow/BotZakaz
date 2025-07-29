from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="➕ Создать слоты на 14 дней", callback_data="create_slots"),
        InlineKeyboardButton(text="📅 Просмотреть бронирования", callback_data="view_records"),
    ],
])