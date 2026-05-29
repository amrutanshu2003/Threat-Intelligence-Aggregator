# Threat Intelligence Aggregator (Non-AI)

## 1. Project Overview / Description
Threat Intelligence Aggregator (Non-AI) ek practical blue-team toolkit hai jo multiple threat feeds se Indicators of Compromise (IOCs) collect karta hai, unhe normalize karta hai, repeated indicators correlate karta hai, aur actionable outputs generate karta hai.

Project AI/ML use nahi karta. Iska focus deterministic parsing, validation, correlation, aur blocklist generation par hai.

## 2. Practical Motivation
Security teams ko alag-alag sources se threat data milta hai:
- Open-source intelligence feeds
- CERT advisories
- SIEM/Firewall/EDR logs

Problem:
- Har feed ka format alag hota hai
- Duplicate aur noisy IOC data hota hai
- Rapid response ke liye consolidated view chahiye hota hai

Solution:
- Single pipeline jo ingest, parse, normalize, correlate aur export kare

## 3. Project Objectives
- Multiple IOC feeds ingest karna (file/URL)
- IOC parse karna (`ip`, `domain`, `url`, `hash`, `email`)
- Unified schema me normalize karna
- Cross-feed repeated indicators detect karna
- Severity assign karna (`Low`, `Medium`, `High`)
- Blocklist aur final report export karna

## 4. Practical Scope of the Project
### 4.1 IOC Feed Parser
- Supported formats: `CSV`, `TXT`, `JSON`, `STIX`
- Input mode: uploaded files and configured feeds
- Invalid/duplicate handling

### 4.2 Normalization Engine
- Fields: `indicator`, `ioc_type`, `source`, `category`, `ingested_at`
- Standardized lowercase IOC representation

### 4.3 Correlation Engine
- Key: `(indicator, ioc_type)`
- Source frequency aur mention count calculate karta hai
- Severity rules:
  - `High`: source_count >= 5
  - `Medium`: source_count >= 3
  - `Low`: otherwise

### 4.4 Blocklist Generator
- Firewall IP blocklist
- Web domain/URL blocklist
- EDR hash blocklist
- Export: `TXT`, `CSV`, `JSON`

### 4.5 Reporting Module
- Feed processing summary
- Total normalized indicators
- Total unique correlated indicators
- Severity breakdown
- High-priority indicators list

## 5. Tools & Technologies Used
- Language: Python
- Core libraries: `re`, `json`, `csv`, `ipaddress`, `urllib`, `sqlite3`
- Storage: SQLite (`data/ti_aggregator.db`)
- Interface: Python HTTP web app (`webapp.py`)

## 6. Practical Techniques Implemented
- IOC extraction with regex + validation
- Heterogeneous feed normalization
- Cross-source correlation
- Severity prioritization
- Defensive blocklist generation
- Structured report export

## 7. Workflow / Architecture
1. Load feeds  
2. Parse indicators  
3. Normalize and validate  
4. Correlate repeated indicators  
5. Generate blocklists  
6. Export final report and datasets

## 8. Flowchart (Text Version)
START  
-> Load IOC Feeds  
-> Parse Indicators  
-> Normalize & Validate Data  
-> Correlation Engine (Cross-Feed Matching)  
-> Generate Blocklists  
-> Export Final TI Report  
-> END

## 9. Expected Practical Output
Toolkit generates:
- Normalized IOC database
- Parsed IOC dataset by type
- Correlation results
- Blocklists ready for enforcement
- Final threat report

## 10. Actual Output Files (Current Build)
- `outputs/normalized_iocs.json`
- `outputs/normalized_iocs.csv`
- `outputs/parsed_iocs_by_type.json`
- `outputs/correlated_iocs.json`
- `outputs/correlated_iocs.csv`
- `outputs/firewall_ip_blocklist.txt`
- `outputs/web_blocklist.txt`
- `outputs/edr_hash_blocklist.txt`
- `outputs/threat_report.json`
- `outputs/threat_report.txt`
- `data/ti_aggregator.db`

## 11. Learning Outcomes
- IOC structure and validation
- Threat feed ingestion patterns
- Practical SOC correlation workflow
- Blocklist-driven defensive operations

## 12. Project Deliverables
- Working toolkit (code + web interface)
- Correlation output files
- Blocklist files
- Final TI report
- Documentation (this file to Word/PDF)
- Presentation slides (see `docs\PPT_OUTLINE.md`)
- Screenshots checklist (see `docs\SCREENSHOT_CHECKLIST.md`)

## 13. How to Run
```powershell
python webapp.py
```
Open:
`http://127.0.0.1:8000`

## 14. Conclusion
Threat Intelligence Aggregator (Non-AI) successfully demonstrates end-to-end defensive threat-intel automation using deterministic parsing and correlation. It is practical for internship showcase and blue-team workflow demonstration.
