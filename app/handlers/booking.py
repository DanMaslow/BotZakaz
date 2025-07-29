from aiogram import Router, types
from app.keyboards.client_kb import client_kb

router = Router()

@router.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери действие ниже:", reply_markup=client_kb)