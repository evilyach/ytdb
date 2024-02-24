import asyncio
import logging

from app import main
from app.config import Settings
from app.logger import configure_logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    settings = Settings()

    configure_logging(settings.logging_level)
    logger.info(settings)

    asyncio.run(main(settings))
