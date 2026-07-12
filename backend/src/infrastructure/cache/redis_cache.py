import json
from typing import Any, Optional

import redis.asyncio as redis

from src.core.config import get_settings

settings = get_settings()


class RedisCache:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.default_ttl = 300  # 5 минут

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Сохранить значение в кеш"""
        ttl = ttl or self.default_ttl
        # Преобразуем SQLAlchemy объекты в dict
        if hasattr(value, "__dict__"):
            # Убираем SQLAlchemy внутренние поля
            data = {k: v for k, v in value.__dict__.items() if not k.startswith("_sa_")}
            await self.client.setex(key, ttl, json.dumps(data, default=str))
        else:
            await self.client.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        """Удалить значение из кеша"""
        await self.client.delete(key)

    async def clear_pattern(self, pattern: str) -> None:
        """Удалить все ключи по паттерну"""
        keys = await self.client.keys(pattern)
        if keys:
            await self.client.delete(*keys)

    async def close(self) -> None:
        """Закрыть соединение"""
        await self.client.close()
