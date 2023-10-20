import logging
from typing import TYPE_CHECKING, Any, Coroutine

from pyrogram.types import Message

from .domain import DownloadFormat

if TYPE_CHECKING:
    from app.telegram.domain import CustomTelegramClient


def get_download_tasks(
    _: "CustomTelegramClient",
    message: Message,
    info_list: list[dict[str, Any]],
    download_format: DownloadFormat = DownloadFormat.VIDEO,
) -> list[Coroutine[Any, Any, Message | None]]:
    return [
        message.reply_audio(
            audio=info.get("filepath", None),
            title=info.get("title", None),
            performer=info.get("artist", None),
            duration=info.get("duration", None),
        )
        if download_format == DownloadFormat.AUDIO
        else message.reply_video(
            video=info.get("filepath", None),
            caption=info.get("title", None),
            width=info.get("width", None),
            height=info.get("height", None),
            supports_streaming=True,
        )
        for info in info_list
    ]
