from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def build_summary(
    feed_stats: list[dict[str, Any]],
    normalized_count: int,
    unique_count: int,
    correlation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    high_rows = [row for row in correlation_rows if row["severity"] == "High"]
    medium_rows = [row for row in correlation_rows if row["severity"] == "Medium"]
    low_rows = [row for row in correlation_rows if row["severity"] == "Low"]

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "feeds_processed": feed_stats,
        "total_normalized_iocs": normalized_count,
        "total_unique_iocs": unique_count,
        "severity_breakdown": {
            "High": len(high_rows),
            "Medium": len(medium_rows),
            "Low": len(low_rows),
        },
        "high_priority_indicators": high_rows[:100],
    }


def export_report(summary: dict[str, Any], out_dir: str) -> dict[str, str]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / "threat_report.json"
    json_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    text_file = output_dir / "threat_report.txt"
    lines = [
        "Threat Intelligence Aggregator Final Report",
        "=" * 45,
        f"Generated At: {summary['generated_at']}",
        "",
        "Feed Processing Summary:",
    ]

    for feed in summary["feeds_processed"]:
        lines.append(
            f"- {feed['name']}: status={feed['status']}, rows={feed.get('rows', 0)}, iocs={feed.get('iocs', 0)}"
        )

    lines.extend(
        [
            "",
            f"Total Normalized IOCs: {summary['total_normalized_iocs']}",
            f"Total Unique Correlated IOCs: {summary['total_unique_iocs']}",
            "Severity Breakdown:",
            f"- High: {summary['severity_breakdown']['High']}",
            f"- Medium: {summary['severity_breakdown']['Medium']}",
            f"- Low: {summary['severity_breakdown']['Low']}",
            "",
            "Top High-Priority Indicators:",
        ]
    )

    for row in summary["high_priority_indicators"][:20]:
        lines.append(
            f"- {row['indicator']} ({row['ioc_type']}) | sources={','.join(row['sources'])} | mentions={row['total_mentions']}"
        )

    text_file.write_text("\n".join(lines), encoding="utf-8")

    return {"report_json": str(json_file), "report_txt": str(text_file)}
