import os
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT : str

    ADMIN_IDS: list[int]

    LOG_PATH : str = "data/log.txt" # ДОБАВИТЬ / перед data
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    STORE_URL: str = "sqlite+aiosqlite:///data/my_base.sqlite" # 4 слеша! перед деплоем
    PROXY : str

    BASE_URL : str

    API_KEY : str

    FLAGCREATE : int
    FLAGDROP : int

    @property
    def get_webhook(self):
        return f"{self.BASE_URL}/webhook"


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )
setting = Settings()

log_file = setting.LOG_PATH
logger.add(log_file, level="INFO", format=setting.FORMAT_LOG, rotation=setting.LOG_ROTATION)