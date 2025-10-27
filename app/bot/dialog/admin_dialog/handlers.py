from typing import Any

from aiogram import types
from aiogram.types import FSInputFile
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from loguru import logger

from app.bot.dialog.admin_dialog.state import AdminPanelBanner
from app.config import setting
from app.dao.dao import BannerDao


async def on_check_admin_menu(call : types.CallbackQuery, widget : Any, dialog_manager : DialogManager, item_id : str):
    try:
        if item_id == "Изменить баннер":
            await dialog_manager.start(state=AdminPanelBanner.add_banner_state)


    except Exception as e:
        logger.error(f"Ошибка в on_check_admin_menu : {e}")

async def add_image_banner(message : types.Message, widget :  MessageInput, dialog_manager : DialogManager):
    try:
        select_banner = message.photo[-1].file_id
        session = dialog_manager.middleware_data["session_with_commit"]
        await BannerDao(session).update(name = "menu", values = select_banner)
        logger.info("Баннер успешно добавлен")
        await dialog_manager.done()
    except Exception as e:
        logger.error(f"Ошибка в add_image_banner : {e}")