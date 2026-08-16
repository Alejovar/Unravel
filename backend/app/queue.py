from functools import lru_cache

import redis
from rq import Queue

from app.config import get_settings

QUEUE_NAME = "unravel-analyses"


@lru_cache
def get_redis_connection() -> redis.Redis:
    settings = get_settings()
    return redis.from_url(settings.redis_url)


@lru_cache
def get_queue() -> Queue:
    return Queue(QUEUE_NAME, connection=get_redis_connection(), default_timeout=900)
