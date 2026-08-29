from aiogram.fsm.state import State, StatesGroup


class NodeSetupStates(StatesGroup):
    waiting_ip = State()
    waiting_ssh_user = State()
    waiting_ssh_password = State()
    waiting_cert = State()
    confirming = State()
    installing = State()
