from __future__ import annotations

import ipaddress
import re
from typing import Any

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
URL_RE = re.compile(r"\bhttps?://[^\s,\"'<>]+", re.IGNORECASE)
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")
EMAIL_RE = re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")
HASH_RE = re.compile(r"\b(?:[A-Fa-f0-9]{32}|[A-Fa-f0-9]{40}|[A-Fa-f0-9]{64})\b")


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _row_to_text(row: dict[str, Any]) -> str:
    return " ".join(str(v) for v in row.values() if v is not None)


def parse_iocs_from_row(row: dict[str, Any]) -> list[dict[str, str]]:
    text = _row_to_text(row)
    extracted: list[dict[str, str]] = []

    for item in IP_RE.findall(text):
        if _is_valid_ip(item):
            extracted.append({"indicator": item, "ioc_type": "ip"})

    for item in URL_RE.findall(text):
        extracted.append({"indicator": item, "ioc_type": "url"})

    for item in EMAIL_RE.findall(text):
        extracted.append({"indicator": item.lower(), "ioc_type": "email"})

    for item in HASH_RE.findall(text):
        extracted.append({"indicator": item.lower(), "ioc_type": "hash"})

    for item in DOMAIN_RE.findall(text):
        if not item.startswith("http") and not _is_valid_ip(item):
            extracted.append({"indicator": item.lower(), "ioc_type": "domain"})

    return extracted
