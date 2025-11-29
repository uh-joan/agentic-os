---
name: get_oncology_recalls_2024
description: >
  Retrieves and analyzes oncology drug recalls from 2024 using FDA enforcement reports.
  Provides comprehensive analysis including recall classification (Class I/II/III),
  recall reasons, affected products, recalling firms, and status. Categorizes by severity
  and analyzes trends in quality control issues. Essential for quality system benchmarking
  and supply chain risk management.
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - data_aggregation
  - classification_analysis
data_scope:
  total_results: 24
  geographical: United States
  temporal: 2024
created: 2025-11-22
complexity: medium
execution_time: ~5 seconds
---
# get_oncology_recalls_2024


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What oncology recalls 2024 drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved oncology recalls 2024 medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for oncology recalls 2024`


Analyzes oncology drug recalls from 2024 to identify quality control issues and supply chain risks.

## Key Findings

**Total Recalls**: 24 in 2024
**Classification**:
- Class II (Moderate Risk): 23 recalls
- Class III (Low Risk): 1 recall

**Primary Recall Reason**: Particle contamination (CGMP deviations)

**Most Affected Manufacturer**: Fosun Pharma USA Inc.

**Affected Products**:
- Doxorubicin Hydrochloride Injection (multiple concentrations)
- Gemcitabine Injection
- Leucovorin Calcium Injection (multiple concentrations)

## Business Applications

- Quality system benchmarking against industry standards
- Supply chain risk assessment and mitigation
- Vendor quality management
- Regulatory compliance monitoring
- Manufacturing process improvement identification