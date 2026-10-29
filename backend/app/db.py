"""SQLite storage. One small file on a Docker volume — plenty for one athlete and a few devices."""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "/data/race_plan.db")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    week INTEGER NOT NULL,
    day TEXT NOT NULL,
    phase TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL,
    planned REAL NOT NULL,
    unit TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);

CREATE TABLE IF NOT EXISTS session_logs (
    session_id INTEGER PRIMARY KEY REFERENCES sessions(id),
    status TEXT NOT NULL CHECK (status IN ('done', 'partial', 'skipped')),
    actual REAL,
    effort INTEGER,
    duration_min REAL,
    notes TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habits (
    date TEXT PRIMARY KEY,
    sleep_hours REAL,
    water_litres REAL,
    protein_g INTEGER,
    calories INTEGER,
    veg_servings INTEGER,
    sunlight INTEGER,
    kegel_1 INTEGER,
    kegel_2 INTEGER,
    fast_kept INTEGER,
    energy INTEGER,
    notes TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weeks (
    week INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    date TEXT NOT NULL,
    target_weight REAL,
    stretch_weight REAL,
    planned_long_run REAL,
    planned_swim REAL
);

CREATE TABLE IF NOT EXISTS checkins (
    week INTEGER PRIMARY KEY REFERENCES weeks(week),
    weight REAL,
    waist REAL,
    long_run_actual REAL,
    swim_nonstop_actual REAL,
    energy INTEGER,
    notes TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

# Columns added after the first release. init_db adds any that an older database is missing.
HABIT_EXTRA = {
    "weight": "REAL", "resting_hr": "INTEGER", "sleep_quality": "INTEGER", "soreness": "INTEGER",
    "pain": "INTEGER", "pain_where": "TEXT", "mood": "INTEGER", "motivation": "INTEGER",
    "nutrition": "INTEGER", "fast_tolerance": "INTEGER", "warning_signs": "INTEGER",
}
CHECKIN_EXTRA = {"tt_5k_min": "REAL"}

PLAN_SETTINGS = ("start_date", "week1_date", "race_date", "start_weight", "realistic_loss_per_week",
                 "stretch_weight", "fast_until", "fast_days")


def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def get_conn():
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _add_missing_columns(conn, table, columns):
    have = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
    for name, kind in columns.items():
        if name not in have:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {kind}")


def init_db():
    """Create tables, add new columns, and (re)load the plan. Logs, habits and check-ins are kept.

    If the plan's sessions change shape (a new plan), logs for sessions that no longer exist are removed.
    """
    plan = json.loads((DATA_DIR / "plan.json").read_text())
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        _add_missing_columns(conn, "habits", HABIT_EXTRA)
        _add_missing_columns(conn, "checkins", CHECKIN_EXTRA)

        ids = [s["id"] for s in plan["sessions"]]
        # A session id that now means a different day/type than before carries a stale log: drop it.
        for s in plan["sessions"]:
            old = conn.execute("SELECT date, type FROM sessions WHERE id = ?", (s["id"],)).fetchone()
            if old and (old["date"] != s["date"] or old["type"] != s["type"]):
                conn.execute("DELETE FROM session_logs WHERE session_id = ?", (s["id"],))
        conn.execute(f"DELETE FROM session_logs WHERE session_id NOT IN ({','.join('?' * len(ids))})", ids)
        conn.execute(f"DELETE FROM sessions WHERE id NOT IN ({','.join('?' * len(ids))})", ids)
        conn.executemany(
            """INSERT INTO sessions (id, date, week, day, phase, time_slot, type, title, details, planned, unit)
               VALUES (:id, :date, :week, :day, :phase, :time_slot, :type, :title, :details, :planned, :unit)
               ON CONFLICT(id) DO UPDATE SET date=excluded.date, week=excluded.week, day=excluded.day,
                 phase=excluded.phase, time_slot=excluded.time_slot, type=excluded.type, title=excluded.title,
                 details=excluded.details, planned=excluded.planned, unit=excluded.unit""",
            plan["sessions"],
        )
        wk = [w["week"] for w in plan["weeks"]]
        conn.execute(f"DELETE FROM checkins WHERE week NOT IN ({','.join('?' * len(wk))})", wk)
        conn.execute(f"DELETE FROM weeks WHERE week NOT IN ({','.join('?' * len(wk))})", wk)
        conn.executemany(
            """INSERT INTO weeks (week, label, date, target_weight, stretch_weight, planned_long_run, planned_swim)
               VALUES (:week, :label, :date, :target_weight, :stretch_weight, :planned_long_run, :planned_swim)
               ON CONFLICT(week) DO UPDATE SET label=excluded.label, date=excluded.date,
                 target_weight=excluded.target_weight, stretch_weight=excluded.stretch_weight,
                 planned_long_run=excluded.planned_long_run, planned_swim=excluded.planned_swim""",
            plan["weeks"],
        )
        # Plan settings always follow the plan file (a new plan replaces dates and targets).
        for key in PLAN_SETTINGS:
            if key in plan:
                conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                             (key, json.dumps(plan[key])))


def settings(conn):
    return {r["key"]: json.loads(r["value"]) for r in conn.execute("SELECT key, value FROM settings")}


def reference():
    return json.loads((DATA_DIR / "reference.json").read_text())
