import os
import redis


_redis_host = os.getenv("REDIS_HOST", "localhost")
_redis_port = int(os.getenv("REDIS_PORT", "6379"))
_redis_db = int(os.getenv("REDIS_DB", "0"))
_redis_paasword = os.getenv("REDIS_PASSWORD", "")

redis_conn = redis.Redis(
    host=_redis_host, port=_redis_port, db=_redis_db, password=_redis_paasword
)


expire_time_7_day = 60 * 60 * 24 * 7
