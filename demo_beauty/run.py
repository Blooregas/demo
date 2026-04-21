import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import config
from app.database.engine import init_db, close_db, async_session_maker
from app.middlewares.database import DatabaseSessionMiddleware
from app.handlers import client, llm_chat, profile, admin # Подключим роутер клиента (создадим ниже)

async def main():
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Инициализируем БД при старте
    await init_db()

    # Создаем бота. Используем HTML по умолчанию — это надежнее Markdown
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Регистрируем глобальные мидлвари
    # Теперь в каждый хэндлер будет прилетать аргумент session: AsyncSession
    dp.update.middleware(DatabaseSessionMiddleware(session_pool=async_session_maker))
    # Подключаем роутеры (наши разделенные хэндлеры)
    dp.include_router(admin.router)
    dp.include_router(client.router)
    # Хук на выключение бота (чтобы корректно закрыть соединения с БД)
    dp.shutdown.register(close_db)
    dp.include_router(llm_chat.router)
    dp.include_router(profile.router)
    # Запускаем поллинг, предварительно сбросив зависшие апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную.")