from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


def _fetch_text(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": "TI-Aggregator/1.0"})
    with urlopen(req, timeout=timeout) as response:  # noqa: S310
        return response.read().decode("utf-8", errors="ignore")


def _load_local(path: str) -> str:
    return Path(path).read_text(encoding="utf-8-sig", errors="ignore")


def load_feed_content(feed: dict[str, Any]) -> str:
    source_type = feed.get("source_type", "file")
    location = feed.get("location")
    if not location:
        raise ValueError("Feed missing location")

    if source_type == "url":
        return _fetch_text(location)
    return _load_local(location)


def _parse_stix(raw_text: str) -> list[dict[str, Any]]:
    data = json.loads(raw_text)
    objects = data.get("objects", []) if isinstance(data, dict) else []
    rows: list[dict[str, Any]] = []
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        pattern = obj.get("pattern")
        if pattern:
            rows.append({"line": pattern, "stix_type": obj.get("type", "indicator")})
    return rows


def _parse_csv(raw_text: str) -> list[dict[str, Any]]:
    lines = [line for line in raw_text.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines:
        return []

    try:
        reader = csv.DictReader(lines)
        rows = [dict(row) for row in reader]
        if rows:
            return rows
    except Exception:  # noqa: BLE001
        pass

    return [{"line": line.strip()} for line in lines]


def parse_raw_by_format(raw_text: str, fmt: str) -> list[dict[str, Any]]:
    fmt = (fmt or "txt").lower()

    if fmt == "json":
        data = json.loads(raw_text)
        if isinstance(data, dict):
            data = data.get("data", [data])
        return data if isinstance(data, list) else []

    if fmt == "csv":
        return _parse_csv(raw_text)

    if fmt == "stix":
        return _parse_stix(raw_text)

    if fmt == "txt":
        return [{"line": line.strip()} for line in raw_text.splitlines() if line.strip()]

    return [{"line": line.strip()} for line in raw_text.splitlines() if line.strip()]
