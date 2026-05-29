# Screenshot Checklist

## Web UI Screens
- [ ] Home dashboard loaded (`http://127.0.0.1:8000`)
- [ ] Feed Input form visible (file upload + format)
- [ ] Feed Processing Summary table with statuses
- [ ] Correlation Results table
- [ ] Outputs download section

## Processing Screens
- [ ] Run analysis action in progress (optional)
- [ ] Updated dashboard metrics after run

## Output Evidence Screens
- [ ] `outputs/normalized_iocs.json`
- [ ] `outputs/parsed_iocs_by_type.json`
- [ ] `outputs/correlated_iocs.csv`
- [ ] `outputs/firewall_ip_blocklist.txt`
- [ ] `outputs/web_blocklist.txt`
- [ ] `outputs/edr_hash_blocklist.txt`
- [ ] `outputs/threat_report.txt`
- [ ] `data/ti_aggregator.db`

## Optional Deployment Screens
- [ ] Vercel preview URL
- [ ] Vercel production URL
