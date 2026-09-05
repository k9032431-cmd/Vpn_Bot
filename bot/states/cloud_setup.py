from aiogram.fsm.state import State, StatesGroup


class CloudSetupStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()
    connecting = State()


class CloudServerCreateStates(StatesGroup):
    choosing_zone = State()
    choosing_plan = State()
    choosing_template = State()
    waiting_hostname = State()
    confirming = State()
