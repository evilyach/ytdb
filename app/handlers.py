from typing import TYPE_CHECKING

from yt_dlp.utils import DownloadError, ExtractorError

from .download import download_video

if TYPE_CHECKING:
    from pyrogram import Message, Client


async def start_handler(_: "Client", message: "Message") -> None:
    await message.reply(
        "Send me a link to a YouTube video. You can choose if you want to "
        "download full video, or you just want to download audio from the "
        "video."
    )


async def download_handler(client: "Client", message: "Message") -> None:
    try:
        filename, info = download_video(message.text)
    except (DownloadError, ExtractorError):
        await message.reply(f"Can't download video from {message.text}.")
    else:
        height, width = info.get("height", None), info.get("width", None)

        await client.send_video(
            message.chat.id,
            filename,
            caption=info.get("title", None),
            width=width if width <= 1280 else 1280,
            height=height if height <= 720 else 720,
            supports_streaming=True,
        )

    await client.delete_messages(message.chat.id, message.id)
