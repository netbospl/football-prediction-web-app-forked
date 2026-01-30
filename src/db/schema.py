"""SQLite schema definitions for the football prediction app.

Tables:
- runs: Pipeline/app execution records
- predictions: Model predictions snapshot per run
- trades: Recommended trades per run
- results: Final match outcomes (updated when available)
"""

SCHEMA_SQL = """
-- Runs table: tracks each pipeline or app execution
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    backend TEXT NOT NULL DEFAULT 'local',
    notes TEXT,
    git_sha TEXT
);

-- Predictions table: snapshot of model predictions per run
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    match_key TEXT NOT NULL,
    f_div TEXT,
    f_date TEXT,
    f_time TEXT,
    home_team TEXT,
    away_team TEXT,
    pred_result TEXT,
    pred_diff REAL,
    pred_odds REAL,
    shap_top_json TEXT,
    raw_row_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id),
    UNIQUE(run_id, match_key)
);

-- Trades table: recommended trades per run
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    match_key TEXT NOT NULL,
    side TEXT NOT NULL,
    odds REAL,
    score REAL,
    edge REAL,
    ev REAL,
    stake REAL,
    rationale_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id),
    UNIQUE(run_id, match_key)
);

-- Results table: final match outcomes
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_key TEXT UNIQUE NOT NULL,
    final_result TEXT,
    final_diff REAL,
    home_goals INTEGER,
    away_goals INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_predictions_match_key ON predictions(match_key);
CREATE INDEX IF NOT EXISTS idx_predictions_run_id ON predictions(run_id);
CREATE INDEX IF NOT EXISTS idx_trades_run_id ON trades(run_id);
CREATE INDEX IF NOT EXISTS idx_trades_match_key ON trades(match_key);
CREATE INDEX IF NOT EXISTS idx_results_match_key ON results(match_key);
"""


def create_tables(conn):
    """Create all tables if they don't exist.

    Args:
        conn: sqlite3 connection object
    """
    conn.executescript(SCHEMA_SQL)
    conn.commit()
