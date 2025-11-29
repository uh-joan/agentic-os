---
name: get_anti_amyloid_publications
description: >
  Search PubMed for recent publications on anti-amyloid antibodies for Alzheimer's disease.
  Analyzes publication trends by drug (lecanemab, donanemab, aducanumab, gantenerumab),
  ARIA safety reporting rates, top research institutions, and publication year distribution.
category: scientific-literature
mcp_servers:
  - pubmed_mcp
patterns:
  - pagination
  - json_parsing
  - text_analysis
  - institution_extraction
data_scope:
  total_results: 1438
  geographical: Global
  temporal: 2019-2024 (last 5 years)
created: 2025-11-22
complexity: medium
execution_time: ~8 seconds
---
# get_anti_amyloid_publications


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What's the publication landscape for anti-amyloid antibodies in Alzheimer's?`
2. `@agent-pharma-search-specialist Compare research output for lecanemab, donanemab, and aducanumab`
3. `@agent-pharma-search-specialist How frequently is ARIA safety data reported in anti-amyloid antibody publications?`
4. `@agent-pharma-search-specialist Which institutions are leading research on anti-amyloid antibodies for Alzheimer's?`
5. `@agent-pharma-search-specialist Show me publication trends for gantenerumab and other anti-amyloid therapies`


Search PubMed for recent publications on anti-amyloid antibodies for Alzheimer's disease and analyze research trends, safety reporting, and institutional contributions.

## Key Findings

- 1,438 publications (2019-2024)
- Aducanumab most studied (456 publications)
- ARIA safety data reported in 24.9% of publications
- 2024 publication surge (389 articles) post-approvals
- USC and Harvard lead research (34 and 31 publications)