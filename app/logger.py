import logging
from typing import Self

from rich.logging import RichHandler

logger = logging.getLogger(__name__)


def configure_logging(level: int | str) -> None:
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )


class YtdlpLogger:
    def debug(self: Self, msg: str) -> None:
        logger.info(msg)

    def info(self: Self, msg: str) -> None:
        logger.info(msg)

    def warning(self: Self, msg: str) -> None:
        logger.warning(msg)

    def error(self: Self, msg: str) -> None:
        logger.error(msg)

    def critical(self: Self, msg: str) -> None:
        logger.critical(msg)
