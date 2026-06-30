
# utils/logger.py — Centralised logging using loguru

import sys
from loguru import logger
from config import LOGS_DIR, LOG_LEVEL

# Remove default handler
logger.remove()

# Console handler — coloured, readable
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    colorize=True,
)

# File handler
logger.add(
    LOGS_DIR / "codeis.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
)

def get_logger(name: str):
    """Return a named logger bound to a specific module."""
    return logger.bind(name=name)
