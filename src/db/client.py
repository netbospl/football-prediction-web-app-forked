"""SQLite database client helpers."""

import json
import logging
import os
import sqlite3
import subprocess
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..utils.config import Config as cfg
from .schema import create_tables


# Configure logging
logger = logging.getLogger(__name__)

# Thread-local storage for connections
_local = threading.local()


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


def get_db() -> sqlite3.Connection:
    """Get a thread-local database connection, creating tables if needed.

    Uses thread-local storage to ensure each thread has its own connection,
    avoiding SQLite threading issues.

    Returns:
        sqlite3.Connection: Database connection for current thread
    """
    if not hasattr(_local, 'connection') or _local.connection is None:
        # Ensure directory exists
        db_dir = os.path.dirname(cfg.DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        _local.connection = sqlite3.connect(cfg.DB_PATH)
        _local.connection.row_factory = sqlite3.Row
        create_tables(_local.connection)
        logger.debug(f"Created new database connection for thread {threading.current_thread().name}")
    return _local.connection


def init_db() -> sqlite3.Connection:
    """Initialize the database (create tables if not exist).

    Returns:
        sqlite3.Connection: Initialized database connection
    """
    conn = get_db()
    create_tables(conn)
    logger.info(f"Database initialized at {cfg.DB_PATH}")
    return conn


def close_db() -> None:
    """Close the database connection for the current thread."""
    if hasattr(_local, 'connection') and _local.connection is not None:
        _local.connection.close()
        _local.connection = None
        logger.debug(f"Closed database connection for thread {threading.current_thread().name}")


def _get_git_sha():
    """Get current git commit SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


def create_run(notes: Optional[str] = None) -> int:
    """Create a new run record and return its ID.

    Args:
        notes: Optional notes about the run

    Returns:
        The run ID
    """
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO runs (backend, notes, git_sha) VALUES (?, ?, ?)",
        (cfg.STORAGE_BACKEND, notes, _get_git_sha())
    )
    conn.commit()
    return cursor.lastrowid


def get_latest_run() -> Optional[Dict[str, Any]]:
    """Get the most recent run record."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def save_predictions(run_id: int, df: pd.DataFrame, raise_on_error: bool = False) -> int:
    """Save predictions to the database.

    Args:
        run_id: The run ID to associate with
        df: DataFrame with prediction data
        raise_on_error: If True, raise exception on first error; otherwise log and continue

    Returns:
        Number of rows successfully inserted

    Raises:
        DatabaseError: If raise_on_error is True and an error occurs
    """
    conn = get_db()
    count = 0
    errors = []

    for _, row in df.iterrows():
        match_key = _make_match_key(row)

        # Extract top SHAP features
        shap_top = _extract_top_shap(row)

        # Format date consistently
        date_val = row.get("F_DATE")
        if pd.notna(date_val):
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)[:10]
        else:
            date_str = None

        try:
            conn.execute(
                """INSERT OR REPLACE INTO predictions
                   (run_id, match_key, f_div, f_date, f_time, home_team, away_team,
                    pred_result, pred_diff, pred_odds, shap_top_json, raw_row_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    match_key,
                    row.get("F_DIV"),
                    date_str,
                    row.get("F_TIME"),
                    row.get("F_H_TEAM"),
                    row.get("F_A_TEAM"),
                    cfg.PRED_MAPPING.get(row.get("PRED_RESULT_NUM")),
                    row.get("PRED_DIFF"),
                    row.get("PRED_ODDS"),
                    json.dumps(shap_top),
                    row.to_json()
                )
            )
            count += 1
        except Exception as e:
            error_msg = f"Error saving prediction for {match_key}: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
            if raise_on_error:
                raise DatabaseError(error_msg) from e

    conn.commit()

    if errors:
        logger.warning(f"Saved {count}/{len(df)} predictions with {len(errors)} errors")
    else:
        logger.info(f"Saved {count} predictions for run {run_id}")

    return count


def save_trades(run_id: int, trades: List[Dict[str, Any]], raise_on_error: bool = False) -> int:
    """Save recommended trades to the database.

    Args:
        run_id: The run ID to associate with
        trades: List of trade dictionaries
        raise_on_error: If True, raise exception on first error; otherwise log and continue

    Returns:
        Number of rows successfully inserted

    Raises:
        DatabaseError: If raise_on_error is True and an error occurs
    """
    conn = get_db()
    count = 0
    errors = []

    for trade in trades:
        match_key = trade.get("match_key", "unknown")
        try:
            conn.execute(
                """INSERT OR REPLACE INTO trades
                   (run_id, match_key, side, odds, score, edge, ev, stake, rationale_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    match_key,
                    trade.get("side"),
                    trade.get("odds"),
                    trade.get("score"),
                    trade.get("edge"),
                    trade.get("ev"),
                    trade.get("stake"),
                    json.dumps(trade.get("rationale", {}))
                )
            )
            count += 1
        except Exception as e:
            error_msg = f"Error saving trade for {match_key}: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
            if raise_on_error:
                raise DatabaseError(error_msg) from e

    conn.commit()

    if errors:
        logger.warning(f"Saved {count}/{len(trades)} trades with {len(errors)} errors")
    else:
        logger.info(f"Saved {count} trades for run {run_id}")

    return count


def save_result(match_key: str, final_result: str, final_diff: float,
                home_goals: int = None, away_goals: int = None) -> bool:
    """Save or update a match result.

    Args:
        match_key: Unique match identifier
        final_result: "H", "D", or "A"
        final_diff: Goal difference (home - away)
        home_goals: Home team goals
        away_goals: Away team goals

    Returns:
        True if successful
    """
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO results (match_key, final_result, final_diff, home_goals, away_goals, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(match_key) DO UPDATE SET
                   final_result = excluded.final_result,
                   final_diff = excluded.final_diff,
                   home_goals = excluded.home_goals,
                   away_goals = excluded.away_goals,
                   updated_at = excluded.updated_at""",
            (match_key, final_result, final_diff, home_goals, away_goals, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving result for {match_key}: {e}")
        return False


def get_predictions(run_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Get predictions from the database.

    Args:
        run_id: Filter by run ID (None for latest run)
        limit: Maximum number of records

    Returns:
        List of prediction dictionaries
    """
    conn = get_db()
    if run_id is None:
        run = get_latest_run()
        run_id = run["id"] if run else None

    if run_id is None:
        return []

    rows = conn.execute(
        "SELECT * FROM predictions WHERE run_id = ? ORDER BY f_date DESC, f_time DESC LIMIT ?",
        (run_id, limit)
    ).fetchall()
    return [dict(row) for row in rows]


def get_trades(run_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Get trades from the database.

    Args:
        run_id: Filter by run ID (None for latest run)
        limit: Maximum number of records

    Returns:
        List of trade dictionaries
    """
    conn = get_db()
    if run_id is None:
        run = get_latest_run()
        run_id = run["id"] if run else None

    if run_id is None:
        return []

    rows = conn.execute(
        "SELECT * FROM trades WHERE run_id = ? ORDER BY score DESC LIMIT ?",
        (run_id, limit)
    ).fetchall()
    return [dict(row) for row in rows]


def get_trade_performance() -> Dict[str, Any]:
    """Calculate trade performance metrics by joining trades with results.

    Returns:
        Dictionary with performance metrics
    """
    conn = get_db()

    # Join trades with results
    rows = conn.execute(
        """SELECT t.*, r.final_result, r.final_diff
           FROM trades t
           LEFT JOIN results r ON t.match_key = r.match_key
           WHERE r.final_result IS NOT NULL"""
    ).fetchall()

    if not rows:
        return {"total_trades": 0, "settled_trades": 0}

    total_stake = 0
    total_return = 0
    wins = 0

    for row in rows:
        stake = row["stake"] or 1.0
        total_stake += stake

        # Check if trade was correct
        if row["side"] == row["final_result"]:
            total_return += stake * (row["odds"] or 1.0)
            wins += 1

    settled = len(rows)
    return {
        "total_trades": conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0],
        "settled_trades": settled,
        "wins": wins,
        "losses": settled - wins,
        "win_rate": wins / settled if settled > 0 else 0,
        "total_stake": total_stake,
        "total_return": total_return,
        "roi": (total_return - total_stake) / total_stake if total_stake > 0 else 0
    }


def _make_match_key(row) -> str:
    """Create a unique match key from a row."""
    date_str = str(row.get("F_DATE", ""))[:10]  # YYYY-MM-DD format
    return f"{date_str}_{row.get('F_DIV')}_{row.get('F_H_TEAM')}_{row.get('F_A_TEAM')}"


def _extract_top_shap(row, top_n: int = 5) -> Dict[str, float]:
    """Extract top N positive and negative SHAP values from a row.

    Args:
        row: DataFrame row with SHAP columns
        top_n: Number of top features to extract

    Returns:
        Dictionary with feature names and SHAP values
    """
    shap_cols = [c for c in row.index if c.startswith("SHAP_") and c != "SHAP_INTERCEPT"]

    if not shap_cols:
        return {}

    shap_values = [(col, row[col]) for col in shap_cols if pd.notna(row[col]) and row[col] != 0]

    # Sort by absolute value
    shap_values.sort(key=lambda x: abs(x[1]), reverse=True)

    # Take top N
    result = {}
    for col, val in shap_values[:top_n]:
        feature_name = col.replace("SHAP_", "")
        result[feature_name] = round(val, 4)

    return result
