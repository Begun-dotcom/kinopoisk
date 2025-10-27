from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from loguru import logger

from app.bot.dialog.admin_dialog.dialog import admin_panel, admin_banner
from app.bot.dialog.user_dialog.dialog import select_language, main_menu, select_category, input_search, select_top, \
    show_random, show_movies_actor, user_room
from app.bot.handlers.user_handler import user_router
from app.config import setting
from app.dao.middleware import DatabaseMiddlewareWithCommit, DatabaseMiddlewareWithoutCommit

bot = Bot(token=setting.BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

async def bot_command():
    command = [BotCommand(command="start", description="Запуск KinoPoisk")]
    await bot.set_my_commands(commands=command, scope=BotCommandScopeDefault())

async def start_bot():
    try:
        await bot_command()
        dp.update.middleware(DatabaseMiddlewareWithCommit())
        dp.update.middleware(DatabaseMiddlewareWithoutCommit())
        dp.include_router(user_router)
        dp.include_router(select_language)
        dp.include_router(main_menu)
        dp.include_router(select_category)
        dp.include_router(input_search)
        dp.include_router(select_top)
        dp.include_router(show_random)
        dp.include_router(show_movies_actor)
        dp.include_router(admin_panel)
        dp.include_router(admin_banner)
        dp.include_router(user_room)

        setup_dialogs(dp)
        try:
            for user in setting.ADMIN_IDS:
               await bot.send_message(chat_id=user, text="🤖 Бот запущен!!!\nДля начала работы нажмите /start")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления об обновлении!!! {e}")

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")



async def stop_bot():
    try:
        for admin in setting.ADMIN_IDS:
           await bot.send_message(chat_id=admin, text="Бот остановлен")

    except Exception as e:
        logger.error(f"Ошибка при остановке бота: {e}")