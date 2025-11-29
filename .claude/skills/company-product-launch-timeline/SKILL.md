---
name: analyze_company_product_launch_timeline
description: >
  Correlate FDA device approvals with clinical trials to analyze product launch timelines and commercialization strategy for medical device companies. Imports and combines two dependency skills to identify products with supporting clinical evidence, calculate trial-to-approval timelines, and assess pipeline strength.
category: regulatory
mcp_servers:
  - fda_mcp
  - ct_gov_mcp
patterns:
  - cli_arguments
  - multi_skill_composition
  - data_correlation
  - fuzzy_matching
  - temporal_analysis
dependencies:
  - get_company_fda_device_approvals
  - get_company_clinical_trials_portfolio
data_scope:
  total_results: Variable (36 correlated products for Boston Scientific cardiovascular 2020-2025)
  geographical: Global
  temporal: Configurable (default: 2020-present)
created: 2025-11-25
last_updated: 2025-11-25
complexity: complex
execution_time: ~30 seconds
token_efficiency: ~99% reduction vs raw data
parameters:
  company_name:
    type: string
    required: true
    description: Company name (e.g., "Boston Scientific", "Medtronic")
  focus_area:
    type: string
    required: false
    description: Therapeutic area filter (e.g., "cardiovascular")
  start_year:
    type: integer
    required: false
    default: 2020
    description: Analysis start year
  end_year:
    type: integer
    required: false
    default: current_year
    description: Analysis end year
cli_enabled: true
---
# analyze_company_product_launch_timeline



## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What analyze company product launch timeline drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved analyze company product launch timeline medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for analyze company product launch timeline`


## CLI Usage

```bash
# Default example (Boston Scientific, all areas, since 2020)
python analyze_company_product_launch_timeline.py "Boston Scientific"

# With therapeutic focus
python analyze_company_product_launch_timeline.py "Medtronic" --focus-area neurology

# Custom date range
python analyze_company_product_launch_timeline.py "Abbott" --start-year 2022 --end-year 2024
```

## Parameters

- **company_name** (str, required): Company name
- **--focus-area** (str, optional): Therapeutic area filter
- **--start-year** (int, optional): Analysis start year (default: 2020)
- **--end-year** (int, optional): Analysis end year (default: current year)

## Returns

Correlated FDA approvals and clinical trials with timeline analysis.
## Purpose
Correlate FDA device approvals with supporting clinical trials to understand product development timelines, approval paths, and commercialization strategy for medical device companies.

## Key Features
- Multi-skill composition: Imports two dependency skills for comprehensive analysis
- Fuzzy matching: Correlates trials to approvals using similarity scoring
- Timeline visualization: Shows products with supporting trials chronologically
- Strategic insights: Calculates trial-to-approval time, approval pathways, active pipeline

## Usage
```python
from .claude.skills.company_product_launch_timeline.scripts.analyze_company_product_launch_timeline import analyze_company_product_launch_timeline

result = analyze_company_product_launch_timeline(
    company_name="Boston Scientific",
    focus_area="cardiovascular",
    start_year=2020
)

print(result['summary'])
```

## Example Results (Boston Scientific Cardiovascular 2020-2025)
- Total FDA Approvals: 843
- Total Clinical Trials: 1012
- Products with Supporting Trials: 36
- Average Trial-to-Approval Time: 2.4 years
- Active Pipeline: 120 recruiting/active trials
- Notable: FARAPULSE (4 trials), WATCHMAN FLX (5 trials), POLARx (3 trials)

## Dependencies
Requires both:
- `.claude/skills/company-fda-device-approvals/`
- `.claude/skills/company-clinical-trials-portfolio/`