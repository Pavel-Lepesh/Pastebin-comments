import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    """Links uvicorn logs with loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(level, record.getMessage())
