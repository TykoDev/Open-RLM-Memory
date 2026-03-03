import sys

from loguru import logger

from app.core.config import settings


def setup_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.info(f"Logging setup complete. DB_TYPE={settings.DB_TYPE}, OPENAI_BASE_URL={settings.OPENAI_BASE_URL}")
