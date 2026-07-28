from __future__ import annotations

import atexit
import json
import logging
import os
import platform
import sys
import threading
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Any

from core.config.constants import APP_NAME, LOG_ROOT


_LOG_RETENTION_DAYS = 30
_LOG_FILE_PREFIX = "papernest_"
_SESSION_MARKER_NAME = ".active_session.json"
_LOGGING_CONFIGURED = False
_SESSION_CLOSED = False
_SESSION_CRASHED = False
_SESSION_ID = ""
_SESSION_STARTED_AT: datetime | None = None
_CURRENT_LOG_PATH: Path | None = None
_PREVIOUS_SYS_EXCEPTHOOK = sys.excepthook
_PREVIOUS_THREAD_EXCEPTHOOK = threading.excepthook


class _SafeExtraFormatter(logging.Formatter):
    """Formatter that keeps multiline exceptions readable in the daily log."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return message.replace("\r\n", "\n")


def configure_logging() -> Path:
    """Configure one daily log file and start a clearly delimited session."""
    global _LOGGING_CONFIGURED
    global _SESSION_ID
    global _SESSION_STARTED_AT
    global _CURRENT_LOG_PATH

    if _LOGGING_CONFIGURED and _CURRENT_LOG_PATH is not None:
        return _CURRENT_LOG_PATH

    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    _cleanup_old_logs(LOG_ROOT)

    _SESSION_ID = uuid.uuid4().hex[:8]
    _SESSION_STARTED_AT = datetime.now()
    _CURRENT_LOG_PATH = _daily_log_path(_SESSION_STARTED_AT.date())

    formatter = _SafeExtraFormatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        filename=_CURRENT_LOG_PATH,
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    _LOGGING_CONFIGURED = True
    _install_exception_hooks()
    atexit.register(shutdown_logging)

    logger = logging.getLogger(__name__)
    previous_session = _read_active_session_marker()
    if previous_session is not None:
        logger.warning(
            "La session précédente semble s'être terminée anormalement "
            "(session=%s, démarrage=%s).",
            previous_session.get("session_id", "inconnue"),
            previous_session.get("started_at", "inconnu"),
        )

    _write_active_session_marker()
    _log_session_header(logger)
    return _CURRENT_LOG_PATH


def shutdown_logging() -> None:
    """Close the current session once and flush all logging handlers."""
    global _SESSION_CLOSED

    if not _LOGGING_CONFIGURED or _SESSION_CLOSED:
        return

    _SESSION_CLOSED = True
    logger = logging.getLogger(__name__)

    if _SESSION_CRASHED:
        logger.critical(
            "SESSION %s TERMINÉE APRÈS UNE EXCEPTION NON GÉRÉE.",
            _SESSION_ID,
        )
    else:
        elapsed = _session_duration_seconds()
        logger.info(
            "SESSION %s FERMÉE NORMALEMENT | durée=%ss",
            _SESSION_ID,
            elapsed,
        )
        _remove_active_session_marker()

    _log_separator(logger)
    logging.shutdown()


def get_current_log_path() -> Path:
    """Return the log file used by the current day/session."""
    if _CURRENT_LOG_PATH is not None:
        return _CURRENT_LOG_PATH
    return _daily_log_path(date.today())


def _daily_log_path(day: date) -> Path:
    return LOG_ROOT / f"{_LOG_FILE_PREFIX}{day.isoformat()}.log"


def _cleanup_old_logs(log_root: Path) -> None:
    cutoff = date.today() - timedelta(days=_LOG_RETENTION_DAYS)

    for path in log_root.glob(f"{_LOG_FILE_PREFIX}*.log"):
        log_date = _date_from_log_name(path)
        if log_date is None:
            continue
        if log_date < cutoff:
            try:
                path.unlink()
            except OSError:
                pass


def _date_from_log_name(path: Path) -> date | None:
    raw_date = path.stem.removeprefix(_LOG_FILE_PREFIX)
    try:
        return date.fromisoformat(raw_date)
    except ValueError:
        return None


def _session_marker_path() -> Path:
    return LOG_ROOT / _SESSION_MARKER_NAME


def _read_active_session_marker() -> dict[str, Any] | None:
    marker_path = _session_marker_path()
    if not marker_path.exists():
        return None

    try:
        content = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {"session_id": "inconnue", "started_at": "inconnu"}

    return content if isinstance(content, dict) else None


def _write_active_session_marker() -> None:
    if _SESSION_STARTED_AT is None:
        return

    payload = {
        "session_id": _SESSION_ID,
        "started_at": _SESSION_STARTED_AT.isoformat(timespec="seconds"),
        "pid": os.getpid(),
        "log_file": str(get_current_log_path()),
    }

    try:
        _session_marker_path().write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        logging.getLogger(__name__).warning(
            "Impossible d'écrire le marqueur de session active."
        )


def _remove_active_session_marker() -> None:
    marker_path = _session_marker_path()
    if not marker_path.exists():
        return

    try:
        current = _read_active_session_marker()
        if current is None or current.get("session_id") == _SESSION_ID:
            marker_path.unlink(missing_ok=True)
    except OSError:
        logging.getLogger(__name__).warning(
            "Impossible de supprimer le marqueur de session active."
        )


def _install_exception_hooks() -> None:
    sys.excepthook = _handle_unhandled_exception
    threading.excepthook = _handle_thread_exception


def _handle_unhandled_exception(
    exception_type: type[BaseException],
    exception: BaseException,
    traceback: TracebackType | None,
) -> None:
    global _SESSION_CRASHED
    _SESSION_CRASHED = True

    logging.getLogger(__name__).critical(
        "Exception non gérée dans le thread principal.",
        exc_info=(exception_type, exception, traceback),
    )

    if _PREVIOUS_SYS_EXCEPTHOOK not in (None, _handle_unhandled_exception):
        _PREVIOUS_SYS_EXCEPTHOOK(exception_type, exception, traceback)


def _handle_thread_exception(args: threading.ExceptHookArgs) -> None:
    global _SESSION_CRASHED
    _SESSION_CRASHED = True

    thread_name = args.thread.name if args.thread is not None else "inconnu"
    logging.getLogger(__name__).critical(
        "Exception non gérée dans le thread '%s'.",
        thread_name,
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )

    if _PREVIOUS_THREAD_EXCEPTHOOK not in (None, _handle_thread_exception):
        _PREVIOUS_THREAD_EXCEPTHOOK(args)


def _log_session_header(logger: logging.Logger) -> None:
    _log_separator(logger)
    logger.info(
        "%s | SESSION %s DÉMARRÉE | pid=%s",
        APP_NAME,
        _SESSION_ID,
        os.getpid(),
    )
    logger.info(
        "Environnement | Windows=%s | Python=%s | machine=%s",
        platform.platform(),
        platform.python_version(),
        platform.machine() or "inconnue",
    )
    logger.info("Journal du jour | %s", get_current_log_path())
    _log_separator(logger)


def _log_separator(logger: logging.Logger) -> None:
    logger.info("=" * 88)


def _session_duration_seconds() -> int:
    if _SESSION_STARTED_AT is None:
        return 0
    return max(0, int((datetime.now() - _SESSION_STARTED_AT).total_seconds()))
