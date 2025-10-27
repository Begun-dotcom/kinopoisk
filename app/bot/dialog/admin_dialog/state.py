from aiogram.fsm.state import StatesGroup, State


class AdminPapel(StatesGroup):
    admin_menu = State()

class AdminPanelBanner(StatesGroup):
    add_banner_state = State()

class AdminPanelStatus(StatesGroup):
    get_user_state = State()