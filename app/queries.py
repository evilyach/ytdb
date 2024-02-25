from typing import Optional

from sqlalchemy import select

from app.db import Base, get_session
from app.models import User


async def add(obj: Base) -> None:
    async with get_session() as session:
        session.add(obj)
        await session.commit()


async def get_user_by_id(user_id: int) -> User | None:
    async with get_session() as session:
        stmt = select(User).filter_by(id=user_id)

        return (await session.execute(stmt)).scalars().one_or_none()


async def is_whitelisted(user_id: int) -> bool:
    async with get_session() as session:
        stmt = select(User).filter_by(id=user_id, is_whitelisted=True)

        return bool((await session.execute(stmt)).scalars().one_or_none())


async def update_user_is_audio_only(user_id: int, value: Optional[bool] = None) -> User:
    if not (user := await get_user_by_id(user_id)):
        raise ValueError(f"User with id = '{user_id}' doesn't exit in the database")

    async with get_session() as session:
        new_value = value if value else not user.is_audio_only

        user.is_audio_only = new_value
        await session.merge(user)
        await session.commit()

        return user
