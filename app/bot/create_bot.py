from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from app.bot.user_handler import user_router
from app.config import setting


bot = Bot(token=setting.BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

async def bot_command():
    command = [BotCommand(command="start", description="Запуск KinoPoisk")]
    await bot.set_my_commands(commands=command, scope=BotCommandScopeDefault())

async def start_bot():
    try:
        await bot_command()
        dp.include_router(user_router)
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