from os import getenv

from pyrogram import filters
from pyrogram.handlers.message_handler import MessageHandler
from pyrogram.handlers.callback_query_handler import CallbackQueryHandler
from pyrogram.sync import idle

from .common.redis import AsyncRedisClient
from .handlers import (
    download_handler,
    switch_extract_audio_setting_handler,
    start_handler,
    switch_to_audio_handler,
    switch_to_video_handler,
)
from .telegram.domain import CustomTelegramClient


def get_app() -> CustomTelegramClient:
    app = CustomTelegramClient(
        getenv("BOT_NAME", ""),
        api_id=getenv("API_ID", ""),
        api_hash=getenv("API_HASH", ""),
        bot_token=getenv("BOT_TOKEN", ""),
    )

    app.add_handler(
        MessageHandler(
            start_handler,
            filters.command("start"),
        )
    )
    app.add_handler(
        MessageHandler(
            switch_extract_audio_setting_handler,
            filters.command("format"),
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            switch_to_video_handler,
            filters.regex("switch_format_to_video_handler"),
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            switch_to_audio_handler,
            filters.regex("switch_format_to_audio_handler"),
        )
    )
    app.add_handler(
        MessageHandler(
            download_handler,
            filters.text & filters.private,
        )
    )

    return app


async def main() -> None:
    app: CustomTelegramClient = get_app()

    app.redis = await AsyncRedisClient(url=getenv("REDIS_URL", ""))

    await app.start()
    await idle()
    await app.stop()
