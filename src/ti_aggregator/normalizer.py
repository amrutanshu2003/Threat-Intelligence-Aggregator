from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def normalize_ioc(item: dict[str, Any], source_name: str, category: str = "unknown") -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "indicator": item["indicator"].strip().lower(),
        "ioc_type": item["ioc_type"],
        "source": source_name,
        "category": category,
        "ingested_at": now,
    }
