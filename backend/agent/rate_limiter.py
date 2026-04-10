import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Tool rate limits: tool_name -> (max_calls, window_seconds)
RATE_LIMIT: dict[str, tuple[int, int]] = {
    "send_email": (100, 3600),     # 100 emails per hour
    "query_database": (200, 60),   # 200 queries per minute
    "create_lead": (50, 3600),     # 50 leads per hour
}

_tracker: dict[str, list[datetime]] = defaultdict(list)


def is_rate_limited(tool: str) -> bool:
    """Return True if the tool has exceeded its rate limit."""
    limit, window = RATE_LIMIT.get(tool, (9999, 1))
    now = datetime.now()
    cutoff = now - timedelta(seconds=window)

    # Prune expired timestamps
    _tracker[tool] = [t for t in _tracker[tool] if t > cutoff]

    if len(_tracker[tool]) >= limit:
        logger.warning(f"[rate_limiter] tool={tool} is RATE LIMITED ({len(_tracker[tool])}/{limit})")
        return True
    return False


def increment_rate(tool: str) -> None:
    """Record a successful tool call timestamp."""
    _tracker[tool].append(datetime.now())
    logger.debug(f"[rate_limiter] tool={tool} count={len(_tracker[tool])}")


def get_rate_status() -> dict:
    """Return current call counts per tool (for debugging/monitoring)."""
    now = datetime.now()
    result = {}
    for tool, (limit, window) in RATE_LIMIT.items():
        cutoff = now - timedelta(seconds=window)
        count = len([t for t in _tracker[tool] if t > cutoff])
        result[tool] = {"current": count, "limit": limit, "window_s": window}
    return result
