import time, os
import redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL)
def allow(key: str, limit: int, window_sec: int) -> bool:
    now = int(time.time())
    pipe = r.pipeline()
    pipe.zadd(key, {str(now): now})
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zcard(key)
    pipe.expire(key, window_sec + 1)
    _, _, count, _ = pipe.execute()
    return count <= limit
