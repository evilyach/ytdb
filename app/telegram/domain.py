from pyrogram.client import Client

from ..common.redis import AsyncRedisClient


class CustomTelegramClient(Client):
    redis: AsyncRedisClient
