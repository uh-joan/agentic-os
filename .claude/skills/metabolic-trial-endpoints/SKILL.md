---
name: get_metabolic_trial_endpoints
description: >
  Analyzes primary endpoints used in metabolic disease trials over the past 5 years.
  Categorizes endpoints by type (HbA1c, weight, cardiovascular, lipids, glucose, etc.),
  tracks regulatory acceptance trends, and identifies temporal patterns. Covers diabetes,
  obesity, metabolic syndrome trials from ClinicalTrials.gov with comprehensive endpoint
  categorization.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - temporal_filtering
  - endpoint_categorization
  - trend_analysis
data_scope:
  total_results: 5439
  geographical: Global
  temporal: Past 5 years (2019-2024)
created: 2025-11-22
complexity: medium
execution_time: ~8 seconds
---

# get_metabolic_trial_endpoints

Analyzes primary endpoint trends in metabolic disease clinical trials to inform trial design optimization and regulatory strategy.

## Key Findings

**Total Trials**: 5,439 trials analyzed
**Top Endpoints**:
- HbA1c (Glycemic Control): 1,634 trials (44.6%)
- Weight/BMI: 1,311 trials (35.8%)
- Cardiovascular Outcomes: 513 trials (14.0%)
- Glucose Monitoring: 442 trials (12.1%)

**Regulatory Insights**:
- HbA1c remains gold standard for diabetes trials
- Cardiovascular endpoints increasing (14%) - reflects FDA/EMA requirements
- Quality of Life only 3.4% as primary endpoint
