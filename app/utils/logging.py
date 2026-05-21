from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(app) -> None:
    level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, level_name, logging.INFO)

    app.logger.setLevel(log_level)

    log_file = app.config.get("LOG_FILE")
    if not log_file:
        return

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(log_path, maxBytes=1_048_576, backupCount=3, encoding="utf-8")
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    if not any(isinstance(existing, RotatingFileHandler) for existing in app.logger.handlers):
        app.logger.addHandler(handler)