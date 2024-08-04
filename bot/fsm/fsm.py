from aiogram.fsm.state import State, StatesGroup


class StartupSG(StatesGroup):
    register = State()


class AddNoteSG(StatesGroup):
    text = State()
    custom_time = State()
    custom_date = State()
