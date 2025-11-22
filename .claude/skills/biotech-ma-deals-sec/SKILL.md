---
name: get_biotech_ma_filings
description: >
  Analyzes biotech M&A activity from SEC EDGAR Form 8-K filings. Searches for current reports
  containing M&A keywords from biotech companies. Provides trend analysis by company and year.
category: financial
mcp_servers:
  - sec_edgar_mcp
patterns:
  - multi_keyword_search
  - deduplication
  - trend_analysis
data_scope:
  total_results: 83
  geographical: US
  temporal: 2020-2024
created: 2025-11-22
complexity: medium
execution_time: ~5 seconds
---

# get_biotech_ma_filings

Biotech merger and acquisition SEC filings analysis.
