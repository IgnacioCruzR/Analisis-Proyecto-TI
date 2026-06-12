import logging
import os

import redis as redis_lib

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

logger = logging.getLogger(__name__)

redis_client: redis_lib.Redis | None = None

try:
    _r = redis_lib.Redis.from_url(_REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _r.ping()
    redis_client = _r
except Exception:
    logger.warning("Redis no disponible en %s — ETL usará fallback síncrono, cache KPI desactivado", _REDIS_URL)
