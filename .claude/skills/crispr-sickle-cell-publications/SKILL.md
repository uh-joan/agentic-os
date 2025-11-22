---
name: get_crispr_sickle_cell_publications
description: >
  Search PubMed for latest publications on CRISPR gene editing for sickle cell disease.
  Analyzes publication trends over time, clinical outcomes data, off-target effects,
  and safety profiles. Context: Covers research leading to and following Casgevy
  (first CRISPR therapy) FDA approval in December 2023.
category: scientific-literature
mcp_servers:
  - pubmed_mcp
patterns:
  - pubmed_search
  - json_parsing
  - trend_analysis
  - keyword_extraction
data_scope:
  total_results: 200
  geographical: Global
  temporal: All time (sorted by date)
created: 2025-11-22
complexity: medium
execution_time: ~3 seconds
---

# get_crispr_sickle_cell_publications

Search and analyze PubMed publications on CRISPR gene editing for sickle cell disease.

## Key Features

- 200 most recent publications on CRISPR + SCD
- Year-over-year publication growth tracking
- Topic coverage analysis (clinical trials, efficacy, safety, off-target effects)
- Recent highlights with clinical/safety tags
- Context: Casgevy FDA approval milestone (Dec 2023)
