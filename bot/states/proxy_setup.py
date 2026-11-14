from aiogram.fsm.state import State, StatesGroup


class ProxySetupStates(StatesGroup):
    waiting_ip = State()
    waiting_ssh_user = State()
    choosing_auth_method = State()
    waiting_ssh_password = State()
    waiting_ssh_key = State()
    confirming = State()
    installing = State()
