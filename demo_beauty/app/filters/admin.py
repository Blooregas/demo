from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.core.config import config

class IsAdmin(BaseFilter):
    """
    Фильтр проверяет, находится ли Telegram ID пользователя 
    в списке ADMIN_IDS из нашего .env файла.
    """
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        return user_id in config.admin_ids