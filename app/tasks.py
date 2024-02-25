import asyncio
import logging
import os
from typing import Any, NamedTuple

import ffmpeg
from pyrogram.client import Client
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.config import settings
from app.models import DownloadEntry, User
from app.queries import add, get_user_by_id

logger = logging.getLogger(__name__)


class HandleUrlTaskData(NamedTuple):
    url: str
    client: Client
    message: Message
    user_id: int
    chat_id: int
    ydl: YoutubeDL


async def get_info_task(data: HandleUrlTaskData) -> dict[str, Any]:
    """Get information about the video."""

    logger.info(f"Downloading the info about '{data.url}'...")

    try:
        info = await asyncio.to_thread(data.ydl.extract_info, data.url, download=False)
    except DownloadError as error:
        logger.error(error)
        logger.error("Can't download info.")

        if "Access restricted" in str(error):
            await data.message.reply("Maybe video is private.")

        raise

    if not info:
        logger.warning(f"No info was downloaded for link: '{data.url}'")
        logger.warning(f"Most likely, link doesn't contain any videos.")

        return {}

    logger.info(f"Got info about '{data.url}'...")

    return info


async def download_video_locally_task(data: HandleUrlTaskData) -> None:
    """Download the video locally."""

    logger.info(f"Downloading the video from '{data.url}' locally...")

    try:
        await asyncio.to_thread(data.ydl.download, [data.url])
    except Exception as error:
        logger.error(error)
        logger.error(f"Couldn't download '{data.url}'!")

        raise

    logger.info(f"Downloaded the video from '{data.url}' locally...")


def get_info_about_file_task(path: str) -> dict:
    """Get information about the video from the file."""

    try:
        data = ffmpeg.probe(path)

        streams = data.get("streams")
        if not streams:
            return {}

        try:
            return streams[0]
        except Exception:
            return {}

    except ffmpeg.Error as error:
        logger.error(error)
        logger.error(f"Couldn't get info from video '{path}'!")

        raise


async def send_video_to_user_task(data: HandleUrlTaskData, info: dict, filepath: str) -> None:
    """Send the video back to the user."""

    logger.info(f"Sending the video '{filepath}' to '{data.chat_id}'...")

    real_info = get_info_about_file_task(filepath)

    title = f'{info.get("title", "Без названия")} ({data.url.strip()})'
    duration = info.get("duration", round(float(real_info.get("duration", "0"))))
    width = info.get("width", real_info.get("width", 0))
    height = info.get("height", real_info.get("height", 0))

    try:
        await data.client.send_video(
            data.chat_id,
            filepath,
            caption=title,
            duration=duration,
            width=width,
            height=height,
            supports_streaming=True,
        )
    except Exception as error:
        logger.error(error)
        logger.error(f"Couldn't send the video '{filepath}' to '{data.chat_id}'!")

        raise

    logger.info(f"Successfully sent '{filepath}' to '{data.chat_id}'...")


async def send_audio_to_user_task(data: HandleUrlTaskData, info: dict, filepath: str) -> None:
    """Send the audio back to the user."""

    logger.info(f"Sending the audio '{filepath}' to '{data.chat_id}'...")

    if not (performer := info.get("artist", None)):
        performer = info.get("channel", info.get("id", "unknown"))

    if not (track := info.get("track", None)):
        track = info.get("title", "unknown")

    try:
        await data.client.send_audio(
            data.chat_id,
            filepath,
            duration=info.get("duration", None),
            performer=performer,
            title=track,
            caption=f'{info.get("title", None)} ({data.url})',
        )
    except Exception as error:
        logger.error(error)
        logger.error(f"Couldn't send the audio '{filepath}' to '{data.chat_id}'!")

        raise


def clean_up_task(video_id: str) -> None:
    """Delete the video."""

    potential_exts = ("mp3", "mp4", "mkv", "webm", "webp", "jpg")
    potential_files = [f"./output/{video_id}.{ext}" for ext in potential_exts]

    for filepath in potential_files:
        try:
            os.remove(filepath)
            logger.info(f"Removed '{filepath}'")
        except OSError:
            continue


async def handle_url_task(data: HandleUrlTaskData) -> None:
    """A task to handle given URL to a video.

    It does a few things:

    1. Gets information about the video.
    2. Downloads a video to a temp folder.
    3. Sends a video back to the user who requested the video.
    4. Deletes the video afterwards.
    """

    logger.info(f"Handling '{data.url}'...")

    info = await get_info_task(data)
    if not info:
        return

    filepath = f"./output/{info['id']}.mp4"
    logger.info(f"{info['id']} - {info.keys() = }")

    await download_video_locally_task(data)
    await send_video_to_user_task(data, info, filepath)

    # Wait before deleting the video to use it as cache
    logger.info(f"Waiting for {settings.video_cache_time} seconds to keep '{data.url}' in cache...")
    if settings.video_cache_time > 0:
        await asyncio.sleep(settings.video_cache_time)

    # Create an entry in the database about the download
    entry = DownloadEntry(user_id=data.user_id, url=data.url, name=info.get("title", None))
    await add(entry)

    clean_up_task(info["id"])

    logger.info(f"Handled '{data.url}' successfully!")


async def register_user_task(user_id: int) -> None:
    if await get_user_by_id(user_id):
        return

    try:
        user = User(id=user_id)
        await add(user)
    except Exception as error:
        logger.error(error)
        logger.error(f"Could not resigster user with id = {user_id}!")

    logger.info(f"Created user with id = {user_id}!")
