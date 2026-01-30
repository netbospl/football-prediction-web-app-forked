"""SQLite database module for persistent storage of runs, predictions, trades, and results."""

from .client import (
    get_db,
    init_db,
    close_db,
    create_run,
    get_latest_run,
    save_predictions,
    save_trades,
    save_result,
    get_predictions,
    get_trades,
    get_trade_performance,
    DatabaseError,
)
from .schema import create_tables

__all__ = [
    "get_db",
    "init_db",
    "close_db",
    "create_tables",
    "create_run",
    "get_latest_run",
    "save_predictions",
    "save_trades",
    "save_result",
    "get_predictions",
    "get_trades",
    "get_trade_performance",
    "DatabaseError",
]
