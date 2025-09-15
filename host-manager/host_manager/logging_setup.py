import logging
import logging.handlers
import os
from typing import Optional


def setup_logging(log_file: str = "/var/log/host-manager/host-manager.log", verbose: bool = False) -> None:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers in idempotent runs
    for h in list(root.handlers):
        root.removeHandler(h)

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    root.addHandler(console)

    rotating = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    rotating.setLevel(level)
    rotating.setFormatter(formatter)
    root.addHandler(rotating)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
