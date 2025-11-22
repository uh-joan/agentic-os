---
name: get_pharma_company_stock_data
description: >
  Retrieves comprehensive stock market data for pharmaceutical companies from Yahoo Finance.
  Collects prices, market cap, P/E ratios, YTD returns, and historical data.
category: financial
mcp_servers:
  - financials_mcp
patterns:
  - json_parsing
  - multi_metric_aggregation
data_scope:
  total_results: 3
  geographical: Global
  temporal: Current + 1 year
created: 2025-11-22
complexity: medium
execution_time: ~5 seconds
---

# get_pharma_company_stock_data

Stock market data for pharmaceutical companies (Pfizer, Merck, J&J).
