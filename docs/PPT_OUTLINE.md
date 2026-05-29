# PPT Outline - Threat Intelligence Aggregator (Non-AI)

## Slide 1 - Title
- Threat Intelligence Aggregator (Non-AI)
- Name, role, date

## Slide 2 - Problem Statement
- Multiple threat feeds
- Inconsistent formats
- Duplicate/noisy IOC data
- Need for actionable defense outputs

## Slide 3 - Objectives
- Ingest multi-format feeds
- Parse and normalize IOCs
- Correlate repeated indicators
- Generate blocklists and reports

## Slide 4 - Architecture
- Feed Loader
- IOC Parser
- Normalization Engine
- Correlation Engine
- Blocklist Generator
- Reporting Module

## Slide 5 - Workflow
- Load feeds
- Parse indicators
- Normalize data
- Correlate across feeds
- Export outputs

## Slide 6 - IOC Types & Validation
- IP
- Domain
- URL
- Hash
- Email

## Slide 7 - Correlation & Severity Logic
- Group by `(indicator, ioc_type)`
- Count sources and mentions
- Severity mapping:
  - High >= 5 sources
  - Medium >= 3 sources
  - Low otherwise

## Slide 8 - Outputs
- Normalized datasets
- Correlated IOC files
- Firewall/Web/EDR blocklists
- Final threat report
- SQLite IOC database

## Slide 9 - Demo Screens
- Web dashboard
- Feed processing summary
- Correlation table
- Output download section

## Slide 10 - Key Results
- Feeds processed
- Normalized IOC count
- Unique correlated indicators
- High severity indicators

## Slide 11 - Learning Outcomes
- Practical threat feed handling
- IOC normalization techniques
- Blue-team automation workflow

## Slide 12 - Conclusion
- Project readiness
- Real-world defensive value
- Future improvements (TAXII, auth, scheduling)
