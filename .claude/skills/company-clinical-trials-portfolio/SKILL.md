---
name: get_company_clinical_trials_portfolio
description: >
  Extract comprehensive clinical trial portfolio for any company sponsor from ClinicalTrials.gov.

  This skill provides a reusable function to analyze any company's clinical trials portfolio with
  flexible filtering capabilities. Perfect for competitive intelligence, portfolio analysis, and
  strategic planning.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - cli_arguments
  - pagination
  - markdown_parsing
  - parameter_based
  - status_aggregation
  - phase_aggregation
data_scope:
  total_results: Varies by sponsor
  geographical: Global
  temporal: Configurable (default: 2020-present)
created: 2025-11-25
last_updated: 2025-11-25
complexity: medium
execution_time: ~2-5 seconds
token_efficiency: ~99% reduction vs raw data
parameters:
  sponsor_name:
    type: string
    required: true
    description: Company/sponsor name (e.g., "Boston Scientific", "Pfizer")
  status:
    type: string
    required: false
    description: Trial status filter (recruiting, completed, etc.)
  condition:
    type: string
    required: false
    description: Condition/disease filter
  phase:
    type: string
    required: false
    description: Trial phase (PHASE1, PHASE2, PHASE3, PHASE4)
  start_year:
    type: integer
    required: false
    default: 2020
    description: Filter trials posted after this year
cli_enabled: true
---
# get_company_clinical_trials_portfolio



## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for company clinical  portfolio?`
2. `@agent-pharma-search-specialist Find active company clinical  portfolio trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for company clinical  portfolio`


## CLI Usage

```bash
# Default example (Boston Scientific)
python get_company_clinical_trials_portfolio.py "Boston Scientific"

# With condition filter
python get_company_clinical_trials_portfolio.py "Novartis" --condition "heart failure"

# With all filters
python get_company_clinical_trials_portfolio.py "Pfizer" --status "recruiting" --phase "PHASE3" --start-year 2022
```

## Parameters

- **sponsor_name** (str, required): Company/sponsor name
- **--status** (str, optional): Trial status filter
- **--condition** (str, optional): Disease/condition filter
- **--phase** (str, optional): Trial phase (PHASE1, PHASE2, PHASE3, PHASE4)
- **--start-year** (int, optional): Filter trials posted after this year (default: 2020)

## Returns

Clinical trials portfolio with phase distribution, status breakdown, and trial details.
## Purpose
Extract and analyze clinical trial portfolios for any company sponsor from ClinicalTrials.gov with flexible filtering options for competitive intelligence and strategic planning.

## Usage
```python
from .claude.skills.company_clinical_trials_portfolio.scripts.get_company_clinical_trials_portfolio import get_company_clinical_trials_portfolio

# Get Boston Scientific AF trials
result = get_company_clinical_trials_portfolio(
    sponsor_name="Boston Scientific",
    condition="atrial fibrillation",
    start_year=2020
)

print(result['summary'])
print(f"Total trials: {result['total_trials']}")
```

## Example Output
```
Clinical Trials Portfolio: Boston Scientific
Total Trials: 28

Filters Applied:
  - start_year: 2020
  - condition: atrial fibrillation

Trials by Status:
  - RECRUITING: 12 (42.9%)
  - COMPLETED: 7 (25.0%)
  - ACTIVE_NOT_RECRUITING: 6 (21.4%)

Trials by Phase:
  - NOT_APPLICABLE: 25 (89.3%)
  - PHASE4: 3 (10.7%)
```

## Performance
- **Execution time**: 2-5 seconds
- **Token efficiency**: ~99% reduction vs raw data
- **Pagination**: Handles up to 10,000 trials