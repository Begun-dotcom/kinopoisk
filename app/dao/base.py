from loguru import logger
from pydantic import BaseModel
from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError
from typing import TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base import Base  # Импортируем из core

T = TypeVar("T", bound=Base)

class BaseDao(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, filters: BaseModel):
        try:
            filter_dict = filters.model_dump(exclude_unset=True)
            self._session.add(self.model(**filter_dict))
            await self._session.flush()
            logger.info(f"Данные в {self.model.__name__} добавлены успешно")
        except Exception as e:
            logger.error(f"Ошибка добавления в таблицу {self.model}: {e}")

