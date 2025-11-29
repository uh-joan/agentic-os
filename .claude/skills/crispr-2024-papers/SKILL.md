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


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are the recent publications on CRISPR gene editing?`
2. `@agent-pharma-search-specialist Find scientific literature about CRISPR gene editing`
3. `@agent-pharma-search-specialist Show me research papers on CRISPR gene editing`


CRISPR research papers from 2024 with journal distribution analysis.