from enum import auto, Enum
from typing import Any, TypedDict


class DownloadFormat(Enum):
    VIDEO = auto()
    AUDIO = auto()


class VideoQuality(Enum):
    DEFAULT = auto()
    HIGH = auto()
    LOW = auto()


class DownloadSettings(TypedDict):
    format: str
    outtmpl: str
    extract_audio: bool
    paths: dict[str, Any]


def get_settings(download_format: DownloadFormat) -> DownloadSettings:
    format = "mp4"

    if download_format == DownloadFormat.AUDIO:
        extract_audio = True
        outtmpl = "%(title)s.mp3"
    else:
        extract_audio = False
        outtmpl = "%(title)s.mp4"

    return DownloadSettings(
        format=format,
        extract_audio=extract_audio,
        paths={
            "temp": "./tmp/",
            "home": "./output/",
        },
        outtmpl=outtmpl,
    )
