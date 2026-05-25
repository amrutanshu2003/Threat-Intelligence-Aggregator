from __future__ import annotations

import json
from pathlib import Path


def load_feed_config(config_path: str) -> list[dict]:
    path = Path(config_path)
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list):
        raise ValueError("Feed config must be a JSON list")
    return payload
