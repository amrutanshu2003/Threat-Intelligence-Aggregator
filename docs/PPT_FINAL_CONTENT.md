# Threat Intelligence Aggregator (Non-AI) - PPT Content

## Slide 1 - Title Slide
**Title:** Threat Intelligence Aggregator (Non-AI)  
**Subtitle:** Practical Blue Team Threat Correlation and Blocklist Automation  
**Presented by:** <Your Name>  
**Department / Institution:** <Your Department / College>  
**Date:** <Submission Date>

---

## Slide 2 - Problem Statement
- Security teams receive threat intelligence from many sources.
- Feeds come in inconsistent formats (CSV, TXT, JSON, STIX).
- Duplicate and noisy IOC data slows response time.
- Teams need a unified and actionable threat view.

**Speaker note:** This project solves the operational gap between raw feed data and defensive action.

---

## Slide 3 - Project Objective
- Collect IOC feeds from files/URLs.
- Parse IOC types: IP, Domain, URL, Hash, Email.
- Normalize all records into one schema.
- Correlate repeated indicators across sources.
- Assign severity (Low/Medium/High).
- Generate blocklists and export a final report.

---

## Slide 4 - System Architecture
**Core Modules**
- Feed Loader
- IOC Parser
- Normalization Engine
- Correlation Engine
- Blocklist Generator
- Reporting Module
- SQLite Storage
- Web Interface

**Speaker note:** The architecture is deterministic and rule-based, with no AI/ML dependency.

---

## Slide 5 - Workflow
1. Load IOC Feeds  
2. Parse Indicators  
3. Normalize & Validate Data  
4. Correlate Across Feeds  
5. Generate Blocklists  
6. Export Final Threat Report

---

## Slide 6 - IOC Parsing and Validation
- Regex-based extraction for IOC patterns.
- IP validation using `ipaddress`.
- Supports:
  - IPv4 indicators
  - Domains
  - URLs
  - Hashes (MD5/SHA1/SHA256 formats)
  - Emails

---

## Slide 7 - Normalization Strategy
**Standard IOC Schema**
- `indicator`
- `ioc_type`
- `source`
- `category`
- `ingested_at`

**Benefits**
- Uniform data model for all feeds
- Easier correlation and reporting
- Better SOC readability

---

## Slide 8 - Correlation and Severity Logic
- Correlation key: `(indicator, ioc_type)`
- Computes:
  - Source count
  - Mention count
- Severity rules:
  - **High:** appears in 5+ sources
  - **Medium:** appears in 3-4 sources
  - **Low:** appears in 1-2 sources

---

## Slide 9 - Blocklist Generation
**Generated Outputs**
- `firewall_ip_blocklist.txt`
- `web_blocklist.txt` (domains/URLs)
- `edr_hash_blocklist.txt`

**Use Case**
- Rapid defensive enforcement in firewall, web filter, and endpoint controls.

---

## Slide 10 - Reporting and Dataset Exports
**Exports**
- `normalized_iocs.json`
- `normalized_iocs.csv`
- `parsed_iocs_by_type.json`
- `correlated_iocs.json`
- `correlated_iocs.csv`
- `threat_report.json`
- `threat_report.txt`
- `ti_aggregator.db`

---

## Slide 11 - Web Interface Demo Points
- Upload IOC file input (CSV/TXT/JSON/STIX)
- Format selection and run analysis
- Feed processing summary table
- Correlation results table
- Output download section

**Speaker note:** Dashboard keeps the complete workflow visible in one place.

---

## Slide 12 - Sample Results (Replace with your current values)
- Feeds processed: `<value>`
- Total normalized IOCs: `<value>`
- Unique correlated indicators: `<value>`
- High severity indicators: `<value>`

**Example findings**
- Repeated malicious IPs across multiple sources
- Consolidated suspicious domain list
- Reused malware hashes across feeds

---

## Slide 13 - Learning Outcomes
- Practical understanding of TI feed processing
- IOC parsing and normalization techniques
- Cross-feed correlation logic
- SOC-oriented prioritization workflow
- Defensive automation through blocklists

---

## Slide 14 - Challenges and Improvements
**Challenges**
- Inconsistent feed structures
- Duplicate/noisy data
- Runtime/deployment constraints in serverless environments

**Future Enhancements**
- TAXII integration
- Role-based dashboard access
- Scheduled job orchestration
- External persistent DB for cloud production

---

## Slide 15 - Conclusion
- Project demonstrates end-to-end practical threat intelligence aggregation.
- Delivers operational outputs, not just raw analysis.
- Suitable for internship showcase and blue-team portfolio.

**Thank You**

