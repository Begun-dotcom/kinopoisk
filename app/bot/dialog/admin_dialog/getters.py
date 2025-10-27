from aiogram_dialog import DialogManager
from loguru import logger

from app.utils.utils import text_admin_kb


async def admin_log_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = "Панель администратора"
        return {"caption" : caption, "text" : text_admin_kb}
    except Exception as e:
        logger.error(f"Ошибка: {e}")

