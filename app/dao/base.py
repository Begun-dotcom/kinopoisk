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