from aiogram.fsm.state import State, StatesGroup


class PanelSetupStates(StatesGroup):
    waiting_url = State()
    waiting_username = State()
    waiting_password = State()
    connecting = State()


class PanelUserCreateStates(StatesGroup):
    waiting_username = State()
    waiting_limits = State()
    confirming = State()


class PanelUserEditStates(StatesGroup):
    waiting_limits = State()
