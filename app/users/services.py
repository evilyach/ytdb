import json
from typing import Any

from ..common.redis import AsyncRedisClient
from ..youtube.domain import DownloadFormat, VideoQuality
from .domain import UserSettings


async def get_user_settings(redis: AsyncRedisClient, id: str) -> dict[str, Any]:
    return json.loads(await redis.get(id))


async def initialise_user(redis: AsyncRedisClient, id: str) -> None:
    if await get_user_settings(redis, id):
        return

    default_settings: UserSettings = UserSettings(
        download_format=DownloadFormat.VIDEO, quality=VideoQuality.DEFAULT
    )

    await redis.set(id, json.dumps(default_settings))


# async def get_video_quality_setting(
#     redis: AsyncRedisClient, id: str
# ) -> VideoQuality:
#     return (await get_user_settings(redis, id)).get(
#         "quality", VideoQuality.DEFAULT
#     )


async def get_download_format_setting(
    redis: AsyncRedisClient, id: str
) -> DownloadFormat:
    return DownloadFormat(
        (await get_user_settings(redis, id)).get(
            "download_format", DownloadFormat.VIDEO.value
        )
    )


async def update_download_format_setting(
    redis: AsyncRedisClient, id: str, download_format: DownloadFormat
) -> None:
    current = await get_user_settings(redis, id)
    current["download_format"] = download_format.value

    await redis.set(id, json.dumps(current))
