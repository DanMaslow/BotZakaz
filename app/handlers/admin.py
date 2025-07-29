from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.crud.client import get_client_by_telegram_id
from app.keyboards.admin_kb import admin_kb
from app.db.sesion import async_session
from app.handlers.admin_fsm import AdminStates

try:
    from aiogram.filters.text import Text
except ImportError:
    class Text:
        def __init__(self, text: str):
            self.text = text
        def __call__(self, event):
            return event.data == self.text

router = Router()

@router.message(Command(commands=["admin"]))
async def admin_menu(message: types.Message):
    async with async_session() as session:
        client = await get_client_by_telegram_id(session, message.from_user.id)
        if client and client.admin:
            await message.answer("Добро пожаловать в админское меню", reply_markup=admin_kb)
        else:
            await message.answer("Доступ запрещён: ты не админ.")

@router.message(Command(commands=["create_slots"]))
async def create_slots_start(message: types.Message, state: FSMContext):
    await message.answer("Сколько слотов в день создать? Введи число (например, 3)")
    await state.set_state(AdminStates.waiting_for_slots_count)

@router.callback_query(Text("create_slots"))
async def on_create_slots(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Сколько слотов в день создать? Введи число (например, 3)")
    await state.set_state(AdminStates.waiting_for_slots_count)
    await callback.answer()

@router.callback_query(Text("view_records"))
async def on_view_records(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отправь дату для просмотра бронирований в формате ГГГГ-ММ-ДД")
    await state.set_state(AdminStates.waiting_for_booking_date)
    await callback.answer()