from typing import Any

from aiogram import types
from aiogram.types import FSInputFile
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from loguru import logger

from app.bot.dialog.admin_dialog.state import AdminPanelBanner, AdminUserCount, AdminRec
from app.config import setting
from app.dao.dao import BannerDao, UserDao
from app.utils.schemas import  SUserLangOne


async def on_check_admin_menu(call : types.CallbackQuery, widget : Any, dialog_manager : DialogManager, item_id : str):
    try:
        if item_id == "Изменить баннер":
            await dialog_manager.start(state=AdminPanelBanner.select_table_state)
        elif item_id == "Пользователи":
            await dialog_manager.start(state=AdminUserCount.get_user_state)
        elif item_id == "Получить лог":
            from app.bot.create_bot import bot
            for admin in setting.ADMIN_IDS:
                await bot.send_document(chat_id=admin, document=FSInputFile(path=setting.LOG_PATH))
        elif item_id == "Реклама":
            await dialog_manager.start(state=AdminRec.set_rec_state)
    except Exception as e:
        logger.error(f"Ошибка в on_check_admin_menu : {e}")

async def select_table(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, table: str):
    try:
        dialog_manager.dialog_data["table"] = table
        await dialog_manager.switch_to(AdminPanelBanner.add_banner_state)
    except Exception as e:
        logger.error(f"Ошибка в select_table : {e}")

async def add_image_banner(message : types.Message, widget :  MessageInput, dialog_manager : DialogManager):
    try:
        table = dialog_manager.dialog_data["table"]
        select_banner = message.photo[-1].file_id
        session = dialog_manager.middleware_data["session_with_commit"]
        await BannerDao(session).update(name = table, values = select_banner)
        logger.info("Баннер успешно добавлен")
        await dialog_manager.done()
    except Exception as e:
        logger.error(f"Ошибка в add_image_banner : {e}")


async def set_rec(message: types.Message, dialog_: Any, manager: DialogManager, rec: str):
    try:
        from app.bot.create_bot import bot
        session = manager.middleware_data["session_without_commit"]
        get_all_users = await UserDao(session).get_user_id(filters=SUserLangOne(language = "ru"))
        print(get_all_users)
        for user in get_all_users:
            await bot.send_message(chat_id=user, text=rec)

    except Exception as e:
        await message.answer("❌ Произошла ошибка повторите позже!!!")
        logger.error(f"Ошибка в set_rec : {e}")