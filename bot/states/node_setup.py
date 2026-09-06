from aiogram.fsm.state import State, StatesGroup


class NodeSetupStates(StatesGroup):
    waiting_ip = State()
    waiting_ssh_user = State()
    choosing_auth_method = State()
    waiting_ssh_password = State()
    waiting_ssh_key = State()
    waiting_cert = State()
    choosing_ports = State()
    waiting_service_port = State()
    waiting_xray_port = State()
    confirming = State()
    installing = State()
