from aiogram.fsm.state import State, StatesGroup

class RegStates(StatesGroup):
    name = State()
    phone = State()