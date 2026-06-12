import os
import sys

import redis as redis_lib

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

redis_client: redis_lib.Redis | None = None

try:
    _r = redis_lib.Redis.from_url(_REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _r.ping()
    redis_client = _r
except Exception:
    if _ENVIRONMENT != "development":
        print(
            f"FATAL: Redis no disponible en {_REDIS_URL}. Se requiere Redis en producción.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
