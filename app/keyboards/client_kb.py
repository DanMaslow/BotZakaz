from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

client_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="📅 Свободные слоты")],
        [KeyboardButton(text="📋 Мои записи")],
    ],
    resize_keyboard=True
)