from aiogram import Router, types
from aiogram.filters import Command
from app.keyboards.client_kb import client_keyboard  # убедись, что в client_kb.py есть client_keyboard

router = Router()

@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери действие:", reply_markup=client_keyboard)