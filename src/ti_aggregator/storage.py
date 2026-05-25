from __future__ import annotations

import sqlite3
import os
from pathlib import Path
from typing import Any


DB_PATH = Path(os.getenv("TI_DATA_DIR", "data")) / "ti_aggregator.db"


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS iocs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator TEXT NOT NULL,
                ioc_type TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                seen_count INTEGER NOT NULL DEFAULT 1,
                UNIQUE(indicator, ioc_type, source)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at TEXT NOT NULL,
                config_path TEXT,
                feeds_total INTEGER,
                normalized_total INTEGER,
                unique_correlated INTEGER,
                inserted_new INTEGER,
                updated_existing INTEGER
            )
            """
        )
        conn.commit()

    return path


def persist_iocs(normalized_iocs: list[dict[str, Any]], db_path: Path | None = None) -> dict[str, int]:
    path = init_db(db_path)
    inserted_new = 0
    updated_existing = 0

    with sqlite3.connect(path) as conn:
        for row in normalized_iocs:
            cur = conn.execute(
                """
                INSERT INTO iocs (indicator, ioc_type, source, category, first_seen, last_seen, seen_count)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(indicator, ioc_type, source) DO UPDATE SET
                    category = excluded.category,
                    last_seen = excluded.last_seen,
                    seen_count = iocs.seen_count + 1
                """,
                (
                    row["indicator"],
                    row["ioc_type"],
                    row["source"],
                    row.get("category", "unknown"),
                    row["ingested_at"],
                    row["ingested_at"],
                ),
            )
            if cur.rowcount > 0:
                existing = conn.execute(
                    "SELECT seen_count FROM iocs WHERE indicator=? AND ioc_type=? AND source=?",
                    (row["indicator"], row["ioc_type"], row["source"]),
                ).fetchone()
                if existing and existing[0] == 1:
                    inserted_new += 1
                else:
                    updated_existing += 1
        conn.commit()

    return {"inserted_new": inserted_new, "updated_existing": updated_existing}


def persist_run_metadata(
    run_at: str,
    config_path: str,
    feeds_total: int,
    normalized_total: int,
    unique_correlated: int,
    inserted_new: int,
    updated_existing: int,
    db_path: Path | None = None,
) -> None:
    path = init_db(db_path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_at, config_path, feeds_total, normalized_total, unique_correlated, inserted_new, updated_existing
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_at,
                config_path,
                feeds_total,
                normalized_total,
                unique_correlated,
                inserted_new,
                updated_existing,
            ),
        )
        conn.commit()


def clear_run_history(db_path: Path | None = None) -> None:
    path = init_db(db_path)
    with sqlite3.connect(path) as conn:
        conn.execute("DELETE FROM pipeline_runs")
        conn.commit()


def get_db_stats(db_path: Path | None = None) -> dict[str, int]:
    path = init_db(db_path)
    with sqlite3.connect(path) as conn:
        total_iocs = conn.execute("SELECT COUNT(*) FROM iocs").fetchone()[0]
        total_runs = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
    return {"db_total_iocs": total_iocs, "db_total_runs": total_runs}
