import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_DSN: str = "sqlite+aiosqlite:///db.sqlite3"
    BOT_TOKEN: str

    REDIS_URL: str = "redis://redis:6379"
    REDIS_DB: int = 1

    POST_TIME_OPTIONS: list[str] = ["10:00", "14:00", "18:00"]
    POST_BUTTONS: dict[str, str] = {
        "Steam": "https://store.steampowered.com/app/{app_id}/",
        "ProtonDB": "https://www.protondb.com/app/{app_id}/",
        "SteamDB": "https://steamdb.info/app/{app_id}/charts/",
    }


    LOG_DIR: str = "logs"

    LOGGERS: dict[str, str] = {
        "bot": "bot.log",
        "aiogram": "aiogram.log",
        "sqlalchemy.engine": "db.log",
        "urllib3": "requests.log",
    }

    BOT_COMMANDS: dict[str, str] = {
        '/start': 'Start bot|Main menu'
    }

    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()
