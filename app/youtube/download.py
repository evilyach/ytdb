import asyncio
import functools
from asyncio import AbstractEventLoop
from typing import Any, Self

from yt_dlp import YoutubeDL

from .domain import DownloadFormat, DownloadSettings, get_settings


class AsyncYouTubeDownloader:
    def __init__(
        self: Self,
        loop: AbstractEventLoop | None = None,
        download_format: DownloadFormat = DownloadFormat.VIDEO,
    ) -> None:
        self.download_settings: DownloadSettings = get_settings(download_format)

        self.ydl: YoutubeDL = YoutubeDL(self.download_settings)
        self.loop: AbstractEventLoop = loop or asyncio.get_event_loop()

    def extract_info(self: Self, url: str) -> dict[str, Any]:
        return self.ydl.extract_info(url, download=False)

    def download(self: Self, info: dict[str, Any]) -> dict[str, Any]:
        self.ydl.process_info(info)

        return info

    async def get_info_list(
        self: Self, urls: list[str]
    ) -> list[dict[str, Any]]:
        futures = [
            self.loop.run_in_executor(
                None, functools.partial(self.extract_info, url)
            )
            for url in urls
        ]

        return await asyncio.gather(*futures)

    async def download_all(self: Self, urls: list[str]) -> list[dict[str, Any]]:
        info_list = await self.get_info_list(urls)

        futures = [
            self.loop.run_in_executor(
                None, functools.partial(self.download, info)
            )
            for info in info_list
        ]

        return await asyncio.gather(*futures)
