import logging
import logging.config
import os
from pathlib import Path

from config import settings

LOG_FORMAT = "[%(name)s][%(asctime)s] (%(levelname)s) %(filename)s.%(funcName)s.(%(lineno)s) - %(message)s"


def configure_logging(log_dir: str | None = None, loggers: dict[str, str] | None = None) -> None:
    """Configure application logging using ``dictConfig``."""

    if logging.getLogger().handlers:
        return

    loggers = loggers or getattr(settings, "LOGGERS", {})
    log_dir = log_dir or os.getenv("LOG_DIR") or getattr(settings, "LOG_DIR", "logs")
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    handlers: dict[str, dict] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": str(log_path / "app.log"),
            "maxBytes": 10 ** 6,
            "backupCount": 3,
        },
    }

    logger_configs: dict[str, dict] = {}
    for logger_name, file_name in loggers.items():
        handler_name = f"{logger_name.replace('.', '_')}_file"
        handlers[handler_name] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": str(log_path / file_name),
            "maxBytes": 10 ** 6,
            "backupCount": 3,
        }
        logger_configs[logger_name] = {
            "level": "DEBUG",
            "handlers": [handler_name],
            "propagate": False,
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": LOG_FORMAT,
                }
            },
            "handlers": handlers,
            "root": {
                "level": "DEBUG",
                "handlers": ["console", "app_file"],
            },
            "loggers": logger_configs,
        }
    )
