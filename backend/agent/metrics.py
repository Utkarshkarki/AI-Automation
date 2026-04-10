import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

metrics: dict[str, int] = defaultdict(int)
tool_metrics: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
total_runs: int = 0
successful_runs: int = 0


def record_intent(intent: str) -> None:
    """Increment counter for a given intent label."""
    global total_runs
    metrics[intent] += 1
    total_runs += 1
    logger.info(f"[metrics] intent={intent} total={metrics[intent]}")


def record_tool_result(tool: str, status: str) -> None:
    """Track per-tool success/failure counts."""
    global successful_runs
    tool_metrics[tool][status] += 1
    if status == "success":
        successful_runs += 1


def get_metrics() -> dict:
    """Return a snapshot of all current metrics."""
    return {
        "intents": dict(metrics),
        "tools": {t: dict(v) for t, v in tool_metrics.items()},
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "success_rate": round(successful_runs / total_runs, 3) if total_runs > 0 else 0,
    }
