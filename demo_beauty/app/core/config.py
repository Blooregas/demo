from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    admin_ids: list[int] = []
    # По умолчанию юзаем асинхронный SQLite для легкого старта MVP, 
    # но можно подсунуть строку PostgreSQL, и SQLAlchemy схавает её без проблем.
    db_url: str = "sqlite+aiosqlite:///nail_studio.db" 
    llm_api_key: str | None = None

    # Указываем, откуда брать переменные
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Инициализируем конфиг один раз (паттерн Singleton), чтобы импортить `config` везде
config = Settings()