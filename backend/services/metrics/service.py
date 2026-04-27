"""
services/metrics/service.py — PUBLIC API for the Metrics domain.

This is the ONLY file other modules are allowed to import from this package.

To extract into a standalone microservice later:
  1. Deploy services/metrics/ as its own FastAPI app (or swap to Prometheus).
  2. Replace this class body with HTTP calls or a metrics push client.
  3. Nothing else in the codebase needs to change.
"""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Public facade for recording and retrieving runtime metrics.
    Instantiated once in main.py and injected wherever needed.
    """

    def __init__(self):
        self._intents: dict[str, int] = defaultdict(int)
        self._tools: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._total_runs: int = 0
        self._successful_runs: int = 0

    def record_intent(self, intent: str) -> None:
        """Increment the counter for a given intent label and total runs."""
        self._intents[intent] += 1
        self._total_runs += 1
        logger.info(f"[metrics.service] intent={intent} total={self._intents[intent]}")

    def record_tool_result(self, tool: str, status: str) -> None:
        """Track per-tool success/failure counts."""
        self._tools[tool][status] += 1
        if status == "success":
            self._successful_runs += 1

    def get_snapshot(self) -> dict:
        """Return a snapshot of all current metrics."""
        return {
            "intents": dict(self._intents),
            "tools": {t: dict(v) for t, v in self._tools.items()},
            "total_runs": self._total_runs,
            "successful_runs": self._successful_runs,
            "success_rate": (
                round(self._successful_runs / self._total_runs, 3)
                if self._total_runs > 0 else 0
            ),
        }
