from typing import Any, Union

from yt_dlp import YoutubeDL


def download_video(url: str) -> Union[str, dict[str, Any]]:
    settings = {
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

    with YoutubeDL(settings) as ydl:
        info = ydl.extract_info(url, download=False)

        ydl.process_info(info)
        return ydl.prepare_filename(info), info
