---
name: get_crispr_2024_papers
description: >
  Retrieves CRISPR research papers published in 2024 from PubMed with comprehensive metadata.
  Extracts titles, authors, journals, publication dates, DOIs, and abstracts.
category: literature
mcp_servers:
  - pubmed_mcp
patterns:
  - json_parsing
  - date_filtering
data_scope:
  total_results: 487
  geographical: Global
  temporal: 2024/01/01 to 2024/12/31
created: 2025-11-22
complexity: medium
execution_time: ~4 seconds
token_efficiency: 99%
---

# get_crispr_2024_papers

CRISPR research papers from 2024 with journal distribution analysis.
