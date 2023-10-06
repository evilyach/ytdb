from os import getenv

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

from .handlers import start_handler, download_handler


def get_app() -> Client:
    app = Client(
        getenv("BOT_NAME"),
        api_id=getenv("API_ID"),
        api_hash=getenv("API_HASH"),
        bot_token=getenv("BOT_TOKEN"),
    )

    app.add_handler(MessageHandler(start_handler, filters.command("start")))
    app.add_handler(MessageHandler(download_handler, filters.text & filters.private))

    return app
