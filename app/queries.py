from sqlalchemy import select

from app.db import get_session
from app.models import User


async def get_user_by_id(id: int) -> User | None:
    async with get_session() as session:
        stmt = select(User).filter_by(id=id)

        return (await session.execute(stmt)).scalars().one_or_none()


async def create_user(user: User) -> None:
    async with get_session() as session:
        session.add(user)
        await session.commit()


async def is_whitelisted(id: int) -> bool:
    async with get_session() as session:
        stmt = select(User).filter_by(id=id, is_whitelisted=True)

        return bool((await session.execute(stmt)).scalars().one_or_none())
