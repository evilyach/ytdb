import asyncio
import logging
import sys

from pydantic import ValidationError

from app import main
from app.config import Settings
from app.logger import configure_logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        settings = Settings()
    except ValidationError as error:
        logger.error(error)
        sys.exit(1)

    configure_logging(settings.logging_level)
    logger.info(settings)
    asyncio.run(main(settings))
