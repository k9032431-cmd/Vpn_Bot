from aiogram.fsm.state import State, StatesGroup


class CryptStates(StatesGroup):
    waiting_subscription_url = State()
