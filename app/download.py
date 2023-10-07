import asyncio
import functools
from asyncio import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Self, Union

from yt_dlp import YoutubeDL


class AsyncYouTubeDownloader:
    SETTINGS = {
        "format": "mp4",
        "paths": {
            "temp": "./tmp/",
            "home": "./output/",
        },
        "postprocessors": [
            {
                "key": "EmbedThumbnail",
                "already_have_thumbnail": False,
            },
        ],
    }

    def __init__(self: Self, loop: AbstractEventLoop | None = None) -> None:
        self.ydl: YoutubeDL = YoutubeDL(self.SETTINGS)
        self.loop: "AbstractEventLoop" = loop or asyncio.get_event_loop()
        self.ppe: ProcessPoolExecutor = ProcessPoolExecutor()

    def extract_info(self: Self, url: str) -> dict[str, Any]:
        return self.ydl.extract_info(url, download=False)

    async def get_info_list(self: Self, urls: list[str]) -> list[str]:
        futures = [
            self.loop.run_in_executor(None, functools.partial(self.extract_info, url))
            for url in urls
        ]

        return await asyncio.gather(*futures)

    def download(self, info: dict[str, Any]) -> Union[str, str]:
        self.ydl.process_info(info)

        return self.ydl.prepare_filename(info), info

    async def download_all(self: Self, urls: list[str]):
        info_list = await self.get_info_list(urls)

        futures = [
            self.loop.run_in_executor(None, functools.partial(self.download, info))
            for info in info_list
        ]

        return await asyncio.gather(*futures)
