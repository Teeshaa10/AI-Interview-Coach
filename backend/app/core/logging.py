import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """
    Formats every log record as a single line of JSON instead of plain text.

    A line like "2026-01-01 - INFO - user logged in" is fine for a human
    watching a terminal, but a log aggregation tool (Render's log viewer,
    Betterstack, Grafana Loki, etc.) needs structured fields to filter,
    search, and alert on. Emitting JSON from the start costs nothing and
    avoids a painful log-format migration later, once this project needs
    real observability.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    """
    Configures the root logger once, at application startup.

    We attach a single StreamHandler writing to stdout using our
    JSONFormatter. Writing to stdout — not a file — is deliberate: Render
    (and most modern hosts) captures stdout automatically and ships it to
    their log viewer. A local log file would be lost the moment the
    container restarts, since Render's filesystem is ephemeral.

    The log level comes from Settings, so it can differ per environment —
    verbose DEBUG locally, quieter INFO in production — without touching
    code.
    """
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.handlers = [handler]
