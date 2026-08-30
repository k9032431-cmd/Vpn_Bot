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


class PanelNodeCreateStates(StatesGroup):
    waiting_name = State()
    waiting_address = State()
    waiting_port = State()
    confirming = State()


class PanelCoreEditStates(StatesGroup):
    waiting_config = State()
    confirming = State()


class PanelAdminCreateStates(StatesGroup):
    waiting_username = State()
    waiting_password = State()
    confirming = State()


class PanelHostEditStates(StatesGroup):
    waiting_fields = State()
    confirming = State()


class PanelHostCreateStates(StatesGroup):
    waiting_remark = State()
    waiting_address = State()
    waiting_port = State()
    confirming = State()


class PanelInboundEditStates(StatesGroup):
    waiting_fields = State()
    confirming = State()
