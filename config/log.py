import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import settings

LOG_FORMAT = "[%(name)s][%(asctime)s] (%(levelname)s) %(filename)s.%(funcName)s.(%(lineno)s) - %(message)s"


def configure_logging(log_dir: str | None = None, loggers: dict[str, str] | None = None) -> None:
    """Configure application logging."""
    loggers = loggers or getattr(settings, "LOGGERS", {})
    log_dir = log_dir or os.getenv("LOG_DIR") or getattr(settings, "LOG_DIR", "logs")
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(log_path / "app.log", maxBytes=10**6, backupCount=3)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        for name in loggers.keys():
            logging.getLogger(name).setLevel(logging.DEBUG)

    for logger_name, file_name in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(log_path / file_name, maxBytes=10**6, backupCount=3)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
