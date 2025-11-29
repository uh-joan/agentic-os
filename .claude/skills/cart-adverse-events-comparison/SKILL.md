---
name: get_cart_adverse_events_comparison
description: >
  Compare adverse event profiles for all 6 approved CAR-T cell therapies (Kymriah,
  Yescarta, Tecartus, Breyanzi, Abecma, Carvykti). Analyzes cytokine release syndrome
  (CRS) rates, neurotoxicity/ICANS frequencies, and serious adverse events to identify
  safety differentiation opportunities. Uses FDA FAERS database for real-world safety data.
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - multi_product_comparison
  - adverse_event_analysis
data_scope:
  total_results: 6 CAR-T products analyzed
  geographical: Global (FDA FAERS)
  temporal: All reported adverse events
created: 2025-11-22
complexity: medium
execution_time: ~15 seconds
---
# get_cart_adverse_events_comparison


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What CAR-T cell therapy drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved CAR-T cell therapy medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for CAR-T cell therapy`


Provides comprehensive comparative analysis of adverse event profiles for all 6 FDA-approved CAR-T cell therapies.

## CAR-T Products Analyzed

1. Kymriah (tisagenlecleucel) - Novartis
2. Yescarta (axicabtagene ciloleucel) - Kite/Gilead
3. Tecartus (brexucabtagene autoleucel) - Kite/Gilead
4. Breyanzi (lisocabtagene maraleucel) - BMS
5. Abecma (idecabtagene vicleucel) - BMS/bluebird bio
6. Carvykti (ciltacabtagene autoleucel) - J&J/Legend

## Key Metrics

- CRS rates by product
- Neurotoxicity/ICANS frequencies
- Serious adverse event counts
- Safety differentiation opportunities