from aiogram_dialog import DialogManager
from loguru import logger

from app.dao.dao import UserDao
from app.utils.utils import text_admin_kb, banner_text


async def admin_log_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = "Панель администратора"
        return {"caption" : caption, "text" : text_admin_kb}
    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def select_table_getter(dialog_manager: DialogManager, **kwargs):
    try:
        return {"text": banner_text}
    except Exception as e:
        logger.error(f"Ошибка в select_category_getter: {e}")

async def get_status_getter(dialog_manager: DialogManager, **kwargs):
    try:
        session = dialog_manager.middleware_data["session_with_commit"]
        all_user = await UserDao(session).get_all_user()
        text = f"Общее количество пользователей: {all_user}\n"
        return {"text": text}

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"text": "Ошибка"}

