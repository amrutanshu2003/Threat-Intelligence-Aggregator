from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ti_aggregator.blocklist import export_ioc_datasets, generate_blocklists
from ti_aggregator.config import load_feed_config
from ti_aggregator.correlator import correlate_iocs
from ti_aggregator.feed_loader import load_feed_content, parse_raw_by_format
from ti_aggregator.ioc_parser import parse_iocs_from_row
from ti_aggregator.normalizer import normalize_ioc
from ti_aggregator.reporting import build_summary, export_report
from ti_aggregator.storage import get_db_stats, persist_iocs, persist_run_metadata


def run_pipeline(config_path: str, out_dir: str) -> dict:
    feeds = load_feed_config(config_path)
    normalized: list[dict] = []
    feed_stats: list[dict] = []

    for feed in feeds:
        name = feed.get("name", "unknown_feed")
        fmt = feed.get("format", "txt")
        category = feed.get("category", "unknown")

        try:
            raw = load_feed_content(feed)
            rows = parse_raw_by_format(raw, fmt)

            parsed_count = 0
            for row in rows:
                parsed = parse_iocs_from_row(row)
                parsed_count += len(parsed)
                for item in parsed:
                    normalized.append(normalize_ioc(item, source_name=name, category=category))

            feed_stats.append({"name": name, "status": "ok", "rows": len(rows), "iocs": parsed_count})
        except Exception as exc:  # noqa: BLE001
            feed_stats.append({"name": name, "status": "failed", "error": str(exc), "rows": 0, "iocs": 0})

    dedup = {(row["indicator"], row["ioc_type"], row["source"]): row for row in normalized}
    normalized_unique = list(dedup.values())

    correlated = correlate_iocs(normalized_unique)
    dataset_paths = export_ioc_datasets(normalized_unique, out_dir)
    blocklist_paths = generate_blocklists(correlated, out_dir)
    summary = build_summary(feed_stats, len(normalized), len(correlated), correlated)
    report_paths = export_report(summary, out_dir)

    persist_stats = persist_iocs(normalized_unique)
    run_at = datetime.now(timezone.utc).isoformat()
    persist_run_metadata(
        run_at=run_at,
        config_path=config_path,
        feeds_total=len(feeds),
        normalized_total=len(normalized),
        unique_correlated=len(correlated),
        inserted_new=persist_stats["inserted_new"],
        updated_existing=persist_stats["updated_existing"],
    )
    db_stats = get_db_stats()

    return {
        "feed_stats": feed_stats,
        "normalized_total": len(normalized),
        "unique_correlated": len(correlated),
        "db_stats": {**persist_stats, **db_stats},
        "outputs": {**dataset_paths, **blocklist_paths, **report_paths},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Threat Intelligence Aggregator (Non-AI)")
    parser.add_argument("--config", default="examples/feeds.json", help="Path to feed config JSON")
    parser.add_argument("--out", default="outputs", help="Output directory")
    args = parser.parse_args()

    result = run_pipeline(config_path=args.config, out_dir=args.out)

    print("=== Threat Intelligence Aggregator Run Complete ===")
    print(f"Feeds processed: {len(result['feed_stats'])}")
    print(f"Normalized IOC entries: {result['normalized_total']}")
    print(f"Unique correlated indicators: {result['unique_correlated']}")
    print(
        f"DB updates: inserted_new={result['db_stats']['inserted_new']}, "
        f"updated_existing={result['db_stats']['updated_existing']}"
    )
    print(
        f"DB totals: total_iocs={result['db_stats']['db_total_iocs']}, "
        f"total_runs={result['db_stats']['db_total_runs']}"
    )
    print("Output files:")
    for key, path in result["outputs"].items():
        print(f"- {key}: {Path(path).resolve()}")


if __name__ == "__main__":
    main()
