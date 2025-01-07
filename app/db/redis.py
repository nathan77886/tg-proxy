import os
import redis


def create_redis_connection(host="localhost", port=6379, db=0):
    """
    创建 Redis 连接
    :param host: Redis 主机地址
    :param port: Redis 端口号
    :param db: 数据库编号
    :return: Redis 连接对象
    """
    return redis.Redis(host=host, port=port, db=db)


_redis_host = os.getenv("REDIS_HOST", "localhost")
_redis_port = int(os.getenv("REDIS_PORT", "6379"))
_redis_db = int(os.getenv("REDIS_DB", "0"))

redis_conn = create_redis_connection(_redis_host, _redis_port, _redis_db)
