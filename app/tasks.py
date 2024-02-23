import asyncio
import logging
import os
from typing import NamedTuple

from pyrogram.client import Client
from yt_dlp import YoutubeDL

from app.config import settings

logger = logging.getLogger(__name__)


class HandleUrlTaskData(NamedTuple):
    url: str
    client: Client
    user_id: int
    chat_id: int
    ydl: YoutubeDL


async def handle_url_task(data: HandleUrlTaskData) -> None:
    """A task to handle given URL to a video.

    It does a few things:

    1. Gets information about the video.
    2. Downloads a video to a temp folder.
    3. Sends a video back to the user who requested the video.
    4. Deletes the video afterwards.
    """

    logger.info(f"Handling '{data.url}'...")

    # Get information about the video
    logger.info(f"Downloading the info about '{data.url}'...")

    info = await asyncio.to_thread(data.ydl.extract_info, data.url, download=False)
    if not info:
        logger.warning(f"No info was downloaded for link: '{data.url}'")
        logger.warning(f"Most likely, link doesn't contain any videos.")
        return

    filepath = f"./output/{info['id']}.mp4"

    # Download the video locally
    logger.info(f"Downloading the video from '{data.url}' locally...")
    try:
        await asyncio.to_thread(data.ydl.download, [data.url])
    except Exception as error:
        logger.error(error)
        logger.error(f"Couldn't download '{data.url}'!")
        return

    # Send the video back to the user
    logger.info(f"Sending the video from '{data.url}' to '{data.chat_id}'...")
    try:
        await data.client.send_video(
            data.chat_id,
            filepath,
            duration=info.get("duration", None),
            width=info.get("width", None),
            height=info.get("height", None),
            supports_streaming=True,
            caption=f'{info.get("title", None)} ({data.url})',
        )
    except Exception as error:
        logger.error(error)
        logger.error(f"Couldn't send the video '{data.url}' to '{data.chat_id}'!")
        return

    # Wait before deleting the video to use it as cache
    logger.info(f"Waiting for {settings.video_cache_time} seconds to keep '{data.url}' in cache...")
    if settings.video_cache_time > 0:
        await asyncio.sleep(settings.video_cache_time)

    # Delete the video
    try:
        os.remove(filepath)
    except OSError as error:
        logger.error(error)
        logger.error("Something deleted the video before this task ran.")

    logger.info(f"Handled '{data.url}' successfully!")
