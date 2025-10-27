from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.core.database import async_session_maker


class BaseDatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message| CallbackQuery, Dict[str, Any]], Awaitable[Any]],
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