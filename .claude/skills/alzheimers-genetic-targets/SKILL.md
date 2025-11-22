---
name: get_alzheimers_genetic_targets
description: >
  Retrieves genetic targets and drug associations for Alzheimer's disease from Open Targets Platform.
  Queries for disease entity, associated genetic targets with evidence scores, and known drugs.
  Returns top 10 targets ranked by association score with evidence breakdown by data type.
  Use when analyzing Alzheimer's therapeutic targets, drug discovery opportunities, or genetic validation.
  Keywords: Alzheimer's, neurodegeneration, genetic targets, target validation, drug discovery, APOE, APP, PSEN1.
category: target-validation
mcp_servers:
  - opentargets_mcp
patterns:
  - disease_search
  - target_association
  - evidence_aggregation
  - json_parsing
data_scope:
  total_results: 20 targets analyzed
  geographical: Global
  temporal: Current Open Targets data
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~4 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_alzheimers_genetic_targets

Queries Open Targets Platform to retrieve genetic targets associated with Alzheimer's disease.
