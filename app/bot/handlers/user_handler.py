from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from loguru import logger

from app.bot.dialog.user_dialog.state import SelectLanguageState

user_router = Router()

@user_router.message(CommandStart())
async def cms(message : Message, dialog_manager : DialogManager):
    try:
        await dialog_manager.start(state= SelectLanguageState.select_language_state, mode= StartMode.RESET_STACK, data={"user_id" : message.from_user.id})
    except Exception as e:
        logger.error(f"Ошибка в cms {e}")