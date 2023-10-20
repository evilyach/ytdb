from typing import TypedDict
from ..youtube.domain import DownloadFormat, VideoQuality


class UserSettings(TypedDict):
    download_format: DownloadFormat
    quality: VideoQuality
