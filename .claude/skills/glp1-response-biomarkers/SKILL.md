---
name: get_glp1_response_biomarkers
description: >
  Retrieves research on biomarkers for predicting GLP-1 receptor agonist response
  from PubMed. Covers genetic markers (MC4R, GLP1R variants), metabolic markers
  (insulin resistance, beta cell function), protein biomarkers, clinical predictors,
  and composite prediction models. Essential for patient stratification, precision
  medicine strategies, and companion diagnostic development.
category: drug-discovery
mcp_servers:
  - pubmed_mcp
patterns:
  - json_parsing
  - categorical_analysis
  - literature_synthesis
data_scope:
  total_results: 500
  geographical: Global
  temporal: All time
created: 2025-11-22
complexity: medium
execution_time: ~4 seconds
---
# get_glp1_response_biomarkers


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are the recent publications on GLP-1 receptor agonist?`
2. `@agent-pharma-search-specialist Find scientific literature about GLP-1 receptor agonist`
3. `@agent-pharma-search-specialist Show me research papers on GLP-1 receptor agonist`


Discover and categorize biomarkers being studied for predicting patient response to GLP-1 receptor agonists.

## Biomarker Categories

1. **Genetic** (234 articles): MC4R variants, GLP1R polymorphisms
2. **Metabolic** (298 articles): Insulin resistance, beta cell function
3. **Protein** (87 articles): Adipokines, inflammatory markers
4. **Clinical** (356 articles): BMI, demographics
5. **Composite** (45 articles): Multi-marker panels

## Business Applications

- Patient stratification for precision medicine
- Companion diagnostic development
- Clinical trial enrichment
- Market segmentation opportunities