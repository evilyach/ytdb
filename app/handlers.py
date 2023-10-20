import asyncio
import io
from typing import TYPE_CHECKING

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp.utils import DownloadError, ExtractorError

from .youtube.domain import DownloadFormat

from .users.exceptions import NotInitialisedError
from .users.services import (
    get_download_format_setting,
    initialise_user,
    get_user_settings,
    update_download_format_setting,
)
from .youtube.download import AsyncYouTubeDownloader
from .youtube.services import get_download_tasks

if TYPE_CHECKING:
    from pyrogram.types import CallbackQuery, Message

    from .telegram.domain import CustomTelegramClient


async def start_handler(
    client: "CustomTelegramClient", message: "Message"
) -> None:
    await initialise_user(client.redis, str(message.from_user.id))

    await message.reply(
        "Send me a link to a YouTube video. You can choose if you want to "
        "download full video, or you just want to download audio from the "
        "video."
    )


async def download_handler(
    client: "CustomTelegramClient", message: "Message"
) -> None:
    try:
        if not await get_user_settings(client.redis, str(message.from_user.id)):
            raise NotInitialisedError

        download_format = await get_download_format_setting(
            client.redis, str(message.from_user.id)
        )
        ytd = AsyncYouTubeDownloader(download_format=download_format)
        urls = io.StringIO(message.text).readlines()

        info_list = await ytd.download_all(urls)
    except (DownloadError, ExtractorError):
        await message.reply(f"Can't download video from {message.text}.")
    except NotInitialisedError:
        await message.reply("Please run /start before downloading.")
    else:
        await asyncio.gather(
            *get_download_tasks(client, message, info_list, download_format)
        )

    await client.delete_messages(message.chat.id, message.id)


async def switch_to_video_handler(
    client: "CustomTelegramClient", callback_query: "CallbackQuery"
) -> None:
    await update_download_format_setting(
        client.redis, str(callback_query.from_user.id), DownloadFormat.VIDEO
    )


async def switch_to_audio_handler(
    client: "CustomTelegramClient", callback_query: "CallbackQuery"
) -> None:
    await update_download_format_setting(
        client.redis, str(callback_query.from_user.id), DownloadFormat.AUDIO
    )


async def switch_extract_audio_setting_handler(
    client: "CustomTelegramClient", message: "Message"
) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Video",
                    callback_data="switch_format_to_video_handler",
                ),
                InlineKeyboardButton(
                    text="Audio Only",
                    callback_data="switch_format_to_audio_handler",
                ),
            ]
        ]
    )

    await message.reply(
        "Choose if you want to download video or audio", reply_markup=keyboard
    )
