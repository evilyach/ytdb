from typing import Any, Generator, Self

from redis.asyncio import BlockingConnectionPool, Redis


class AsyncRedisClient:
    def __init__(self: Self, url: str) -> None:
        self.local_cache: dict[str, Any] = {}
        self.bcp = BlockingConnectionPool.from_url(url)

    def __await__(self: Self) -> Generator[Self, None, Self]:
        return self.init().__await__()

    async def init(self: Self) -> Self:
        self.pool = await Redis(connection_pool=self.bcp)
        return self

    async def set(self: Self, key: str, value: Any) -> None:
        self.local_cache[key] = value
        await self.pool.set(key, value)

    async def get(self: Self, key: str) -> Any:
        if key in self.local_cache:
            return self.local_cache[key]

        value = await self.pool.get(key)
        if value is not None:
            self.local_cache[key] = value

        return value
