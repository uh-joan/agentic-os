---
name: get_company_fda_device_approvals
description: >
  Extract FDA device approvals (PMA, 510k, device registration) for any medical
  device company over a specified time period. Supports filtering by approval type
  and date range. Automatically deduplicates records and provides comprehensive
  statistics. Use this skill when analyzing medtech company portfolios, competitive
  intelligence, regulatory strategy, or device approval trends.

  Trigger keywords: "FDA device approvals", "medtech company", "510k clearances",
  "PMA approvals", "device registrations", "Boston Scientific", "Medtronic",
  "Abbott devices", "Stryker", "device pipeline"
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - date_filtering
  - deduplication
  - multi_endpoint_aggregation
data_scope:
  total_results: Variable (company-dependent)
  geographical: US FDA
  temporal: Configurable (default: 2020-present)
created: 2025-11-25
last_updated: 2025-11-25
complexity: medium
execution_time: ~5-10 seconds
token_efficiency: ~99% reduction vs raw FDA data
parameters:
  company_name:
    type: string
    required: true
    description: Company name (e.g., "Boston Scientific", "Medtronic")
  start_year:
    type: integer
    required: false
    default: 2020
    description: Start year for filtering
  end_year:
    type: integer
    required: false
    default: current_year
    description: End year for filtering
  device_types:
    type: list
    required: false
    default: ["pma", "510k", "registration"]
    description: Device approval types to include
---
# get_company_fda_device_approvals


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What company fda device approvals drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved company fda device approvals medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for company fda device approvals`


## Purpose
Extract comprehensive FDA device approval data for any medical device company, including PMA approvals, 510(k) clearances, and device registrations. Enables competitive intelligence, regulatory strategy analysis, and portfolio assessment for medtech companies.

## Usage
Use this skill when you need to:
- Analyze a medtech company's regulatory approval history
- Compare device portfolios across competitors
- Track approval trends over time
- Assess regulatory strategy (PMA vs 510k pathway usage)
- Identify recent product launches
- Support M&A due diligence with regulatory data

## Parameters

### Required
- **company_name** (str): Full or partial company name as it appears in FDA databases
  - Examples: "Boston Scientific", "Medtronic", "Abbott", "Stryker"

### Optional
- **start_year** (int): Beginning of date range (default: 2020)
- **end_year** (int): End of date range (default: current year)
- **device_types** (list): Filter by approval type (default: all)
  - Options: "pma", "510k", "registration"

## Output Structure

```python
{
    'company': str,                    # Company name
    'time_period': str,                # "YYYY-YYYY"
    'total_approvals': int,            # Total count
    'approvals_by_type': {
        'PMA': int,                    # Class III devices
        '510k': int,                   # Class I/II devices
        'registration': int            # Device listings
    },
    'approvals': [                     # Sorted by date (newest first)
        {
            'device_name': str,
            'approval_type': str,      # "PMA", "510k", "registration"
            'approval_date': str,      # "YYYY-MM-DD"
            'product_code': str,
            'device_class': str,       # "I", "II", "III"
            'medical_specialty': str,
            'k_number': str or None,
            'pma_number': str or None,
            'applicant': str
        }
    ],
    'summary': str                     # Human-readable summary
}
```

## Example Usage

### Command Line
```bash
# Basic usage (defaults to 2020-present, all types)
python3 .claude/skills/company-fda-device-approvals/scripts/get_company_fda_device_approvals.py "Boston Scientific"

# Custom date range
python3 .claude/skills/company-fda-device-approvals/scripts/get_company_fda_device_approvals.py "Medtronic" 2022 2024
```

### Python Import
```python
from .claude.skills.company_fda_device_approvals.scripts.get_company_fda_device_approvals import get_company_fda_device_approvals

# Get all approvals since 2020
result = get_company_fda_device_approvals(
    company_name="Stryker",
    start_year=2020
)

print(f"Total approvals: {result['total_approvals']}")
```

## Performance
- **Execution time**: 5-10 seconds (depends on company size)
- **Token efficiency**: ~99% reduction vs loading raw FDA data
- **Data freshness**: Real-time from FDA openFDA API