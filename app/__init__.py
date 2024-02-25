import logging

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.handlers.callback_query_handler import CallbackQueryHandler
from pyrogram.handlers.message_handler import MessageHandler
from pyrogram.sync import idle

from app.config import Settings
from app.db import init_db
from app.handlers import (
    download_handler,
    help_handler,
    start_handler,
    toggle_is_audio_only_callback_handler,
    toggle_is_audio_only_handler,
)

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
    app.add_handler(MessageHandler(help_handler, filters.command("help")))
    app.add_handler(MessageHandler(toggle_is_audio_only_handler, filters.command("audio_only")))
    app.add_handler(MessageHandler(download_handler, filters.text & filters.private))
    app.add_handler(CallbackQueryHandler(toggle_is_audio_only_callback_handler, filters.regex("toggle_is_audio_only")))

    await init_db()

    await app.start()
    await idle()
    await app.stop()
