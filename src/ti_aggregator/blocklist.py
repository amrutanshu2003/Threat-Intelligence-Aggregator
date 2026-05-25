from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def ensure_output_dir(path: str) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def generate_blocklists(correlation_rows: list[dict[str, Any]], out_dir: str) -> dict[str, str]:
    out = ensure_output_dir(out_dir)

    ip_rows = [r["indicator"] for r in correlation_rows if r["ioc_type"] == "ip"]
    web_rows = [r["indicator"] for r in correlation_rows if r["ioc_type"] in {"url", "domain"}]
    hash_rows = [r["indicator"] for r in correlation_rows if r["ioc_type"] == "hash"]

    (out / "firewall_ip_blocklist.txt").write_text("\n".join(ip_rows), encoding="utf-8")
    (out / "web_blocklist.txt").write_text("\n".join(web_rows), encoding="utf-8")
    (out / "edr_hash_blocklist.txt").write_text("\n".join(hash_rows), encoding="utf-8")

    with (out / "correlated_iocs.csv").open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["indicator", "ioc_type", "source_count", "total_mentions", "severity", "sources"],
        )
        writer.writeheader()
        for row in correlation_rows:
            temp = dict(row)
            temp["sources"] = ";".join(row["sources"])
            writer.writerow(temp)

    (out / "correlated_iocs.json").write_text(json.dumps(correlation_rows, indent=2), encoding="utf-8")

    return {
        "firewall_ip_blocklist": str(out / "firewall_ip_blocklist.txt"),
        "web_blocklist": str(out / "web_blocklist.txt"),
        "edr_hash_blocklist": str(out / "edr_hash_blocklist.txt"),
        "correlated_csv": str(out / "correlated_iocs.csv"),
        "correlated_json": str(out / "correlated_iocs.json"),
    }


def export_ioc_datasets(normalized_iocs: list[dict[str, Any]], out_dir: str) -> dict[str, str]:
    out = ensure_output_dir(out_dir)
    normalized_json = out / "normalized_iocs.json"
    normalized_csv = out / "normalized_iocs.csv"
    parsed_by_type_json = out / "parsed_iocs_by_type.json"

    normalized_json.write_text(json.dumps(normalized_iocs, indent=2), encoding="utf-8")

    with normalized_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["indicator", "ioc_type", "source", "category", "ingested_at"])
        writer.writeheader()
        writer.writerows(normalized_iocs)

    parsed_by_type: dict[str, list[str]] = {"ip": [], "domain": [], "url": [], "hash": [], "email": []}
    for row in normalized_iocs:
        ioc_type = row.get("ioc_type")
        indicator = row.get("indicator")
        if ioc_type in parsed_by_type and indicator not in parsed_by_type[ioc_type]:
            parsed_by_type[ioc_type].append(indicator)

    parsed_by_type_json.write_text(json.dumps(parsed_by_type, indent=2), encoding="utf-8")

    return {
        "normalized_json": str(normalized_json),
        "normalized_csv": str(normalized_csv),
        "parsed_iocs_by_type": str(parsed_by_type_json),
    }
