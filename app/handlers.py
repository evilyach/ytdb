import asyncio
import io
from typing import TYPE_CHECKING

from yt_dlp.utils import DownloadError, ExtractorError

from .download import AsyncYouTubeDownloader

if TYPE_CHECKING:
    from pyrogram import Client, Message


async def start_handler(_: "Client", message: "Message") -> None:
    await message.reply(
        "Send me a link to a YouTube video. You can choose if you want to "
        "download full video, or you just want to download audio from the "
        "video."
    )


async def download_handler(client: "Client", message: "Message") -> None:
    try:
        ytd = AsyncYouTubeDownloader()
        urls = io.StringIO(message.text).readlines()

        result = await ytd.download_all(urls)
    except (DownloadError, ExtractorError):
        await message.reply(f"Can't download video from {message.text}.")
    else:
        futures = []

        for filename, info in result:
            height, width = info.get("height", None), info.get("width", None)

            futures.append(
                client.send_video(
                    message.chat.id,
                    filename,
                    caption=info.get("title", None),
                    width=width if width <= 1280 else 1280,
                    height=height if height <= 720 else 720,
                    supports_streaming=True,
                )
            )

        await asyncio.gather(*futures)

    await client.delete_messages(message.chat.id, message.id)
