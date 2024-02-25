import logging
from functools import wraps
from typing import Awaitable, Callable

from pyrogram.client import Client
from pyrogram.types import Message

from app.queries import is_whitelisted

logger = logging.getLogger(__name__)

HandlerType = Callable[[Client, Message], Awaitable[None]]


def whitelisted(func: HandlerType) -> HandlerType:
    """Check if user that tries to access the handler is in a whitelist."""

    @wraps(func)
    async def inner(client: Client, message: Message) -> None:
        if not await is_whitelisted(message.from_user.id):
            await client.delete_messages(message.chat.id, message.id)

            logger.warning(f"User with id = {message.from_user.id} tried to access '{func}'!")
            await message.reply("У Вас не доступа к этому ресурсу.")

            return

        await func(client, message)

    return inner
