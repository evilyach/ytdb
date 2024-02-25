import asyncio
import logging
from io import StringIO

from pyrogram.client import Client
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from app.logger import YtdlpLogger
from app.queries import get_user_by_id
from app.security import whitelisted
from app.tasks import HandleUrlTaskData, handle_url_task, register_user_task
from app.validators import validate_url

logger = logging.getLogger(__name__)


async def start_handler(client: Client, message: Message) -> None:
    await client.delete_messages(message.chat.id, message.id)

    if not await get_user_by_id(message.from_user.id):
        await register_user_task(message.from_user.id)
        await message.reply("You are now registered. Contact admin to request access to use this bot.")

    await message.reply(
        "Send me a link to a YouTube video. You can choose if you want to "
        "download full video, or you just want to download audio from the "
        "video."
    )


@whitelisted
async def download_handler(client: Client, message: Message) -> None:
    urls = []

    for url in StringIO(message.text).readlines():
        if not validate_url(url):
            logger.info(f"Tried to download link '{url}', which is not a valid URL.")
            continue

        urls.append(url.strip())

    if not urls:
        logger.info(f"User {message.from_user.id} tried to provide invalid links only.")
        await message.reply("You didn't seem to provide any valid links. Please try again.")

        return

    opts = {
        "format": "mp4/best",
        "logger": YtdlpLogger(),
        "merge_output_format": "mp4",
        "outtmpl": "./output/%(id)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        "writethumbnail": True,
    }

    start_message = await client.send_message(message.chat.id, "Starting the download.")

    with YoutubeDL(opts) as ydl:
        # Get the tasks for downloading the videos
        tasks = [
            handle_url_task(
                HandleUrlTaskData(
                    url=url,
                    client=client,
                    message=message,
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    ydl=ydl,
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

                raise
            finally:
                await client.delete_messages(message.chat.id, start_message.id)
                await client.delete_messages(message.chat.id, message.id)
