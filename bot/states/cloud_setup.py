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
    choosing_auth_method = State()
    waiting_ssh_key = State()
    confirming = State()


class CloudPlanChangeStates(StatesGroup):
    choosing_plan = State()
    confirming = State()


class CloudDiskStates(StatesGroup):
    waiting_size = State()
    confirming_attach = State()
    waiting_resize_size = State()
    confirming_resize = State()


class AzureSetupStates(StatesGroup):
    waiting_tenant_id = State()
    waiting_client_id = State()
    waiting_client_secret = State()
    waiting_subscription_id = State()
    connecting = State()


class AzureVMCreateStates(StatesGroup):
    choosing_location = State()
    choosing_size = State()
    choosing_image = State()
    waiting_hostname = State()
    choosing_auth_method = State()
    waiting_ssh_key = State()
    confirming = State()
