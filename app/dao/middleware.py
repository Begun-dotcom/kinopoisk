from typing import Callable, Dict, Any, Awaitable, Optional

import aiohttp
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from loguru import logger

from app.core.database import async_session_maker


class BaseDatabaseMiddleware(BaseMiddleware):
    async def __call__(self,handler: Callable[[Message| CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            self.set_session(data=data, session=session)
            try:
                result = await handler(event, data)  # Обрабатываем событие
                await self.after_handler(session)  # Дополнительные действия (например, коммит)
                return result
            except Exception as e:
                await session.rollback()  # Откат изменений в случае ошибки
                raise e
            finally:
                await session.close()

    async def set_session(self, data : Dict[str, Any], session):

        raise NotImplementedError()

    async def after_handler(self, session):
        pass

class DatabaseMiddlewareWithoutCommit(BaseDatabaseMiddleware):
    def set_session(self, data : Dict[str, Any], session):
        data['session_without_commit'] = session


class DatabaseMiddlewareWithCommit(BaseDatabaseMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
            data['session_with_commit'] = session

    async def after_handler(self, session) -> None:
            await session.commit()

# ---------------------------

class AiohttpSessionMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        session = await self.get_session()
        data["aiohttp_session"] = session
        return await handler(event, data)

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            logger.debug("🔄 Создание Aiohttp сессии")
            timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_connect=10, sock_read=20)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=20, keepalive_timeout=30)
            self._session = aiohttp.ClientSession(timeout=timeout, connector=connector)
            self._initialized = True
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            logger.debug("❌ Закрытие Aiohttp сессии")
            await self._session.close()


