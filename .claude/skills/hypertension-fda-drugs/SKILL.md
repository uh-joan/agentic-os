---
name: get_hypertension_fda_drugs
description: >
  Retrieves all FDA-approved drugs for hypertension from FDA database.
  Includes brand names, generic names, and manufacturers with deduplication.
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - deduplication
data_scope:
  total_results: 100
  unique_drugs: 45
  geographical: US
  temporal: All FDA approvals
created: 2025-11-22
complexity: medium
execution_time: ~2 seconds
token_efficiency: 99%
---

# get_hypertension_fda_drugs

FDA-approved hypertension drugs with manufacturer information.
