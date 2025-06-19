import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_DSN: str = "sqlite+aiosqlite:///db.sqlite3"
    BOT_TOKEN: str

    REDIS_URL: str = "redis://redis:6379"
    REDIS_DB: int = 1
    TASKIQ_REDIS_DB: int = 2

    LOG_DIR: str = "logs"

    LOGGERS: dict[str, str] = {
        "bot": "bot.log",
        "aiogram": "aiogram.log",
        "sqlalchemy.engine": "db.log",
        "urllib3": "requests.log",
        "taskiq": "taskiq.log",
    }

    BOT_COMMANDS: dict[str, str] = {}

    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
