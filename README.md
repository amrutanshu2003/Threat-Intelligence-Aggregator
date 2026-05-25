# Threat Intelligence Aggregator (Non-AI)

Threat Intelligence Aggregator with website + live feed support + SQLite persistence.

## Data Persistence (Database)
- Database file: `data/ti_aggregator.db`
- Saves all parsed/normalized IOCs with:
  - `indicator`, `ioc_type`, `source`, `category`
  - `first_seen`, `last_seen`, `seen_count`
- Saves pipeline run history in `pipeline_runs`

## Run Website (Sample Feeds)
```powershell
python webapp.py
```

## Deploy on Vercel
This project includes a Vercel Python Function wrapper:

- `api/index.py`
- `vercel.json`

Deploy steps:

```powershell
npm i -g vercel
vercel login
vercel
vercel --prod
```

Vercel note: generated files and SQLite data use temporary serverless storage on Vercel. They are suitable for a demo request, but not guaranteed to persist. For a fully persistent production deployment, use a hosted database/storage service.

## Run Website (Live URL Feeds)
```powershell
$env:TI_CONFIG="examples/live_feeds.json"
python webapp.py
```

## Run CLI (Sample)
```powershell
$env:PYTHONPATH="src"
python src/main.py --config examples/feeds.json --out outputs
```

## Run CLI (Live)
```powershell
$env:PYTHONPATH="src"
python src/main.py --config examples/live_feeds.json --out outputs
```

## Output Files
- `outputs/firewall_ip_blocklist.txt`
- `outputs/web_blocklist.txt`
- `outputs/edr_hash_blocklist.txt`
- `outputs/correlated_iocs.csv`
- `outputs/correlated_iocs.json`
- `outputs/threat_report.json`
- `outputs/threat_report.txt`
