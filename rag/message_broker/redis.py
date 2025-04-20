import aioredis
from typing import Any, Optional
from rag.config import config


class RedisClient:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        self.client = await aioredis.from_url(
            config.redis.get_redis_url,
            db=0,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def close(self) -> None:
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Any:
        if not self.client:
            raise ConnectionError("Redis client is not connected")
        return await self.client.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.client:
            raise ConnectionError("Redis client is not connected")
        return await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> int:
        if not self.client:
            raise ConnectionError("Redis client is not connected")
        return await self.client.delete(key)
    
    async def create_list(self, key: str, values: list) -> int:
        if not self.client:
            raise ConnectionError("Redis client is not connected")
        await self.client.delete(key)
        return await self.client.rpush(key, *values)
    
    async def list_append(self, key: str, value: Any) -> int:
        if not self.client:
            raise ConnectionError("Redis client is not connected")
        return await self.client.rpush(key, value)
        
    async def list_get_all(self, key: str) -> list:
        if not self.client:
            raise ConnectionError("Redis client is not connected")
        return await self.client.lrange(key, 0, -1)