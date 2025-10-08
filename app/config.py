import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT : str

    ADMIN_IDS: list[int]

    LOG_PATH : str = "data/log.txt" # ДОБАВИТЬ / перед data
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    PROXY : str

    BASE_URL : str

    FLAG : int

    @property
    def get_webhook(self):
        return f"{self.BASE_URL}/webhook"
    @property
    def get_url(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )
setting = Settings()

log_file = setting.LOG_PATH
logger.add(log_file, level="INFO", format=setting.FORMAT_LOG, rotation=setting.LOG_ROTATION)