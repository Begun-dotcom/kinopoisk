import os.path
from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from app.bot.create_bot import bot, dp, start_bot, stop_bot

from app.config import setting


@asynccontextmanager
async def lifespan(app : FastAPI):
    try:
        logger.info(f"Попытка запуска бота...!")
        if not os.path.exists("data"):
            os.mkdir("data")
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



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)