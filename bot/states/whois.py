from aiogram.fsm.state import State, StatesGroup


class WhoisStates(StatesGroup):
    waiting_query = State()
