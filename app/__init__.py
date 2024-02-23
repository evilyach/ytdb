import logging

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers.message_handler import MessageHandler
from pyrogram.sync import idle

from app.config import Settings
from app.db import init_db
from app.handlers import download_handler, start_handler

logger = logging.getLogger(__name__)


async def main(settings: Settings) -> None:
    logger.info("Staring the bot...")

    app = Client(
        name=settings.bot_name,
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        bot_token=settings.bot_token,
    )

    app.add_handler(MessageHandler(start_handler, filters.command("start")))
    app.add_handler(MessageHandler(download_handler, filters.text & filters.private))

    await init_db()

    await app.start()
    await idle()
    await app.stop()
