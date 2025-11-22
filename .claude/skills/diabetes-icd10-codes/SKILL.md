---
name: get_diabetes_icd10_codes
description: >
  Retrieves and categorizes all ICD-10 diagnosis codes for diabetes mellitus from NLM Clinical Tables.
  Organizes codes by diabetes type (Type 1, Type 2, gestational, drug-induced, etc.) and complications.
  Useful for clinical documentation, billing analysis, population health queries, and EHR integration.
  Trigger keywords: diabetes ICD-10, diabetes codes, diabetes classification, diabetes diagnosis codes.
category: regulatory
mcp_servers:
  - nlm_codes_mcp
patterns:
  - json_parsing
  - categorization
  - code_classification
data_scope:
  total_results: 200+
  geographical: US (ICD-10-CM)
  temporal: Current ICD-10 version
created: 2025-11-22
last_updated: 2025-11-22
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw code data
---

# get_diabetes_icd10_codes

Retrieves all ICD-10 diagnosis codes for diabetes mellitus and categorizes them by type.
