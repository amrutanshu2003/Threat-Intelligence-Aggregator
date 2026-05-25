from __future__ import annotations

from collections import defaultdict
from typing import Any


def _severity_by_source_count(count: int) -> str:
    if count >= 5:
        return "High"
    if count >= 3:
        return "Medium"
    return "Low"


def correlate_iocs(normalized_iocs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for row in normalized_iocs:
        key = (row["indicator"], row["ioc_type"])
        grouped[key].append(row)

    result: list[dict[str, Any]] = []
    for (indicator, ioc_type), rows in grouped.items():
        sources = sorted({row["source"] for row in rows})
        source_count = len(sources)
        result.append(
            {
                "indicator": indicator,
                "ioc_type": ioc_type,
                "sources": sources,
                "source_count": source_count,
                "total_mentions": len(rows),
                "severity": _severity_by_source_count(source_count),
            }
        )

    result.sort(key=lambda x: (x["source_count"], x["total_mentions"]), reverse=True)
    return result
