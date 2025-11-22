---
name: get_adc_fda_drugs
description: >
  Searches FDA database for antibody-drug conjugate (ADC) approved drugs.
  Uses multi-term search with deduplication to capture comprehensive ADC landscape.
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - deduplication
  - multi_term_search
data_scope:
  total_results: 14
  geographical: US
  temporal: All approvals
created: 2025-11-22
complexity: medium
execution_time: ~5 seconds
token_efficiency: 99%
---

# get_adc_fda_drugs

FDA approved antibody-drug conjugates with approval details.
