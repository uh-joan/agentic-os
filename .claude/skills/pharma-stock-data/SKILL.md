---
name: get_pharma_company_stock_data
description: >
  Retrieves comprehensive stock market data for pharmaceutical companies from Yahoo Finance.
  Collects prices, market cap, P/E ratios, beta, 52-week ranges, and volume data.
  Accepts command-line arguments for ticker symbols.
category: financial
mcp_servers:
  - financials_mcp
patterns:
  - markdown_parsing
  - multi_metric_aggregation
  - cli_arguments
data_scope:
  total_results: Variable (based on input)
  geographical: Global
  temporal: Real-time
created: 2025-11-22
updated: 2025-11-27
complexity: medium
execution_time: ~5 seconds
cli_enabled: true
---
# get_pharma_company_stock_data


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Which companies are working on pharma company stock?`
2. `@agent-pharma-search-specialist Show me the competitive landscape for pharma company stock`
3. `@agent-pharma-search-specialist Who's developing pharma company stock therapies?`


Stock market data for pharmaceutical companies using Yahoo Finance API.

## CLI Usage

```bash
# Default example (PFE, MRK, JNJ)
python get_pharma_company_stock_data.py

# Custom ticker symbols
python get_pharma_company_stock_data.py GILD ABBV BMY

# Single ticker
python get_pharma_company_stock_data.py NVDA
```

## Parameters

- **companies** (list, optional): Ticker symbols (default: ['PFE', 'MRK', 'JNJ'])

## Returns

Stock data including price, change %, market cap, P/E ratio, beta, 52-week high/low.