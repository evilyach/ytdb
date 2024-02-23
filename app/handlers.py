import asyncio
import logging
from io import StringIO

from pyrogram.client import Client
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from app.logger import YtdlpLogger
from app.security import whitelisted
from app.tasks import HandleUrlTaskData, handle_url_task

logger = logging.getLogger(__name__)


@whitelisted
async def start_handler(_: Client, message: Message) -> None:
    await message.reply(
        "Send me a link to a YouTube video. You can choose if you want to "
        "download full video, or you just want to download audio from the "
        "video."
    )


@whitelisted
async def download_handler(client: Client, message: Message) -> None:
    urls = StringIO(message.text).readlines()

    opts = {
        "format": "mp4",
        "logger": YtdlpLogger(),
        "outtmpl": "./output/%(id)s.%(ext)s",
        "writethumbnail": True,
    }

    with YoutubeDL(opts) as ydl:
        # Get the tasks for downloading the videos
        tasks = [
            handle_url_task(
                HandleUrlTaskData(
                    url=url, client=client, chat_id=message.chat.id, user_id=message.from_user.id, ydl=ydl
                )
            )
            for url in urls
        ]

        # Run the tasks
        for task in asyncio.as_completed(tasks):
            try:
                await task
            except Exception:
                await message.reply("Download failed. 😢")
                logger.warning("Error occurred while executing the task.")

    await client.delete_messages(message.chat.id, message.id)
