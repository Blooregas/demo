from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import config
from app.database.models import Base

# Создаем движок. echo=False, чтобы не спамить SQL-запросами в консоль (включим при дебаге)
engine = create_async_engine(url=config.db_url, echo=False)

# Фабрика сессий. expire_on_commit=False обязателен для асинхронной алхимии, 
# чтобы объекты не "протухали" после коммита сессии.
async_session_maker = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """
    Инициализация базы данных.
    Для production-решений здесь должен быть вызов миграций Alembic.
    Но для White-label MVP мы просто генерируем таблицы при старте, если их нет.
    """
    async with engine.begin() as conn:
        # Создаем все таблицы, описанные в моделях
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Корректное закрытие пула соединений при остановке бота"""
    await engine.dispose()