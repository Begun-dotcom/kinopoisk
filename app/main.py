import os.path
from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from app.bot.create_bot import bot, dp, start_bot, stop_bot

from app.config import setting
from app.core.database import create_db, drop_db
from app.utils.utils_func import extract_chat_id_from_update


@asynccontextmanager
async def lifespan(app : FastAPI):
    try:
        logger.info(f"Попытка запуска бота...!")
        if not os.path.exists("data"):
            os.mkdir("data")
        if setting.FLAG_CREATE:
            await create_db()
        if setting.FLAG_DROP:
            await drop_db()
        await start_bot()
        await bot.set_webhook(url=setting.get_webhook,
                              drop_pending_updates=True,
                              allowed_updates=dp.resolve_used_update_types())
        logger.info("Бот запущен!")
        yield
        await stop_bot()

        logger.info("Бот остановлен!")
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def updated(request: Request):
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot=bot, update=update)
        logger.info("Обновления обработаны успешно!")
    except Exception as e:
        logger.error(f"Ошибка обработки обновлений: {e}")

        # Обрабатываем ошибку контекста без зависимости от update_data
        await handle_context_error(e, request)


async def handle_context_error(error: Exception, request: Request):
    """Обрабатывает ошибки контекста"""
    if "Context not found for intent id" in str(error):
        try:
            # Пытаемся получить данные из запроса
            update_data = await request.json()
            chat_id = extract_chat_id_from_update(update_data)

            if chat_id:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Сессия сброшена. Пожалуйста, начните заново /start"
                )
                logger.info(f"Сообщение о сбросе отправлено для chat_id: {chat_id}")
            else:
                logger.warning("Не удалось извлечь chat_id для отправки уведомления")

        except Exception as inner_e:
            logger.error(f"Ошибка при обработке context error: {inner_e}")


#
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)