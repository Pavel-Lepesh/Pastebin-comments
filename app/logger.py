from loguru import logger
import sys
from pathlib import Path


LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


def setup_logger():
    logger.remove()

    logger.add(
        LOGS_DIR / "info.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        LOGS_DIR / "error.log",
        level="ERROR",
        rotation="5 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.add(sys.stdout, level="DEBUG", colorize=True, backtrace=True, diagnose=True)
