from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Открываем сессию
        async with self.session_pool() as session:
            # Кладем сессию в словарь data. 
            # Теперь в любом хэндлере можно написать: async def my_handler(message, session: AsyncSession):
            data["session"] = session
            return await handler(event, data)