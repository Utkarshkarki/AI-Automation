"""
services/email/log.py — Private: JSON-based sent-email log.
Only used internally by EmailService. Not imported by any other domain.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_LOG_PATH = Path(__file__).parent.parent.parent / "sent_emails.json"


def load_log() -> list:
    if _LOG_PATH.exists():
        try:
            with open(_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.warning("[email.log] Could not read sent_emails.json — starting fresh.")
            return []
    return []


def append_to_log(entry: dict) -> None:
    log = load_log()
    log.append(entry)
    with open(_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)
    logger.debug(f"[email.log] Appended entry. Total entries: {len(log)}")


def get_recent(limit: int = 10) -> list:
    return load_log()[-limit:]
