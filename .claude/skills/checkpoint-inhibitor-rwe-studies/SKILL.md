---
name: get_checkpoint_inhibitor_rwe_studies
description: >
  Search PubMed for real-world evidence (RWE) studies on checkpoint inhibitor effectiveness.
  Analyzes real-world performance vs clinical trial efficacy, including real-world response rates,
  survival data (OS, PFS), and patient selection patterns. Covers PD-1, PD-L1, CTLA-4, and
  combination therapies.
category: scientific-literature
mcp_servers:
  - pubmed_mcp
patterns:
  - json_parsing
  - text_analysis
  - study_classification
data_scope:
  total_results: 100
  geographical: Global
  temporal: All time
created: 2025-11-22
complexity: medium
execution_time: ~3 seconds
---
# get_checkpoint_inhibitor_rwe_studies


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are the recent publications on PD-1 checkpoint inhibitor?`
2. `@agent-pharma-search-specialist Find scientific literature about PD-1 checkpoint inhibitor`
3. `@agent-pharma-search-specialist Show me research papers on PD-1 checkpoint inhibitor`


Search PubMed for real-world evidence studies evaluating checkpoint inhibitor effectiveness in clinical practice settings.

## Key Features

- Comprehensive RWE coverage (retrospective, observational, real-world cohorts)
- Multi-target analysis (PD-1, PD-L1, CTLA-4, combinations)
- Study classification by type, cancer, and checkpoint target
- Recent literature highlights
- Effectiveness focus (response rates, survival, patient selection)