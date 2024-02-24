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
