import json
from typing import Dict, Any, List, Optional

import redis

from src import config
from src.libs import app_logger


class RedisCache:
    def __init__(self, rds_client: redis.Redis):
        self._client = rds_client

    def get(self, key: str) -> Dict:
        try:
            content = json.loads(str(self._client.get(key)))
        except Exception as e:
            app_logger.logger.error(f"{e}")
            content = None

        return content

    def set(self, key: str, value: Any, timeout: int = None) -> None:
        if isinstance(value, dict):
            value = json.dumps(value)
        self._client.set(key, value, timeout)

    def hmget(self, name: str, keys: List) -> List:
        return self._client.hmget(name, keys)

    def lrange(self, name: str, start: int, end: int) -> List:
        return self._client.lrange(name, start, end)

    def exists(self, names: str) -> int:
        try:
            return self._client.exists(names)
        except Exception as e:
            app_logger.logger.error(f"{e}")
            return False

    def pipeline(self) -> Any:
        return self._client.pipeline(transaction=False)

    def llen(self, name: str) -> int:
        return self._client.llen(name)

    def hget(self, name: str, key: str) -> Optional[Dict]:
        try:
            res = self._client.hget(name, key)
            return json.loads(str(res))
        except Exception as e:
            app_logger.logger.error(f"{e}")
            return None


def get_connect() -> redis.Redis:
    return redis.StrictRedis.from_url(str(config.REDIS_URI), encoding="utf8", decode_responses=True)


# redis_cache = RedisCache(get_connect())
from werkzeug.local import LocalProxy
proxy_rds_con = LocalProxy(get_connect)
redis_cache = RedisCache(proxy_rds_con)     # type: ignore
