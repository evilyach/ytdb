import logging
from functools import wraps
from typing import Awaitable, Callable

from pyrogram.client import Client
from pyrogram.types import Message

from app.models import User
from app.queries import create_user, get_user_by_id, is_whitelisted

logger = logging.getLogger(__name__)

HandlerType = Callable[[Client, Message], Awaitable[None]]


def whitelisted(func: HandlerType) -> HandlerType:
    """Check if user that tries to access the handler is in a whitelist."""

    @wraps(func)
    async def inner(client: Client, message: Message) -> None:
        if not await get_user_by_id(message.from_user.id):
            user = User(id=message.from_user.id)
            await create_user(user)

            logger.info(f"Created user with id = {message.from_user.id}!")

            await client.delete_messages(message.chat.id, message.id)
            await message.reply("You don't have permission. Contact admin to request access to use this bot.")

            return

        if not await is_whitelisted(message.from_user.id):
            logger.warning(f"User with id = {message.from_user.id} tried to access '{func}'!")
            await message.reply("You don't have permission to access this resource.")

            return

        await func(client, message)

    return inner
