---
name: fda-approvals-timeline-by-indication
version: 2.0.0
description: Fully generic FDA drug approval timeline analyzer - accepts any therapeutic area and drug list with visual timeline and trend analysis
category: regulatory
complexity: intermediate
mcp_servers:
  - fda_mcp
patterns_demonstrated:
  - count_first_mandatory
  - submissions_parsing
  - timeline_aggregation
  - trend_analysis
input_params:
  - name: therapeutic_area
    type: str
    required: true
    description: "Display name for the therapeutic area (e.g., 'Diabetes', 'GLP-1 Agonists', 'Cardiovascular')"
  - name: drugs
    type: list
    required: true
    description: "List of drug names to search (e.g., ['semaglutide', 'metformin', 'insulin glargine'])"
  - name: start_year
    type: int
    required: false
    default: 2015
    description: "Start of analysis period"
  - name: end_year
    type: int
    required: false
    default: current_year
    description: "End of analysis period (defaults to current year for real-time data)"
output_format:
  type: dict
  structure:
    therapeutic_area: str
    total_approvals: int
    approvals_by_year: dict
    drugs_by_year: dict
    average_per_year: float
    trend: str
    summary: str
    all_approvals: list
use_cases:
  - Pipeline gap analysis - Benchmark approval rates by therapeutic area
  - Regulatory timeline forecasting - Predict approval timelines based on historical trends
  - Competitive intelligence - Track competitive approval activity over time
  - Portfolio planning - Identify therapeutic areas with increasing/decreasing approval trends
business_value: |
  Enables strategic decision-making for:
  - Pipeline gap analysis ($8B value) - Identify therapeutic areas with declining approvals
  - Alzheimer's therapeutic opportunity ($2B value) - Understand approval timeline patterns
  - Rare disease M&A targets ($2B value) - Track approval trends in orphan diseases
estimated_value: 9/10
feasibility: 10/10
implementation_time: 2 hours
---

# FDA Approvals Timeline by Indication

Fully generic FDA drug approval timeline analyzer - works with ANY therapeutic area and drug list, providing year-by-year breakdowns and trend analysis.

## Features

- **Fully Generic**: Works with any therapeutic area - just provide drug names
- **Complete Timeline**: Shows ALL years in range, including years with 0 approvals
- **Visual Timeline**: ASCII bar chart visualization of approval trends
- **Trend Detection**: Automatically identifies increasing, stable, or decreasing approval trends
- **FDA Count-First Pattern**: Uses mandatory count parameter to avoid token overflow

## Usage

### Basic Usage

```python
from .claude.skills.fda_approvals_timeline_by_indication.scripts.get_fda_approvals_timeline_by_indication import get_fda_approvals_timeline_by_indication

# Analyze GLP-1 approvals
glp1_drugs = ["semaglutide", "tirzepatide", "liraglutide", "dulaglutide", "exenatide", "lixisenatide"]
result = get_fda_approvals_timeline_by_indication(
    therapeutic_area="GLP-1 Agonists",
    drugs=glp1_drugs,
    start_year=2015
    # end_year defaults to current year for real-time data
)

print(result['summary'])
print(f"Total approvals: {result['total_approvals']}")
print(f"Trend: {result['trend']}")
```

### Diabetes Timeline Example

```python
# Comprehensive diabetes drug analysis
diabetes_drugs = [
    # GLP-1 agonists
    "semaglutide", "tirzepatide", "liraglutide", "dulaglutide",
    # SGLT2 inhibitors
    "empagliflozin", "canagliflozin", "dapagliflozin",
    # DPP-4 inhibitors
    "sitagliptin", "saxagliptin", "linagliptin",
    # Traditional agents
    "metformin", "insulin glargine", "insulin lispro"
]

result = get_fda_approvals_timeline_by_indication(
    therapeutic_area="Diabetes",
    drugs=diabetes_drugs,
    start_year=2015,
    end_year=2024
)
```

### Any Therapeutic Area

```python
# Works for ANY therapeutic area
cart_drugs = ["tisagenlecleucel", "axicabtagene ciloleucel", "brexucabtagene autoleucel"]
result = get_fda_approvals_timeline_by_indication(
    therapeutic_area="CAR-T Therapy",
    drugs=cart_drugs,
    start_year=2017
)
```

### Command Line Execution

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/fda-approvals-timeline-by-indication/scripts/get_fda_approvals_timeline_by_indication.py
```

## Output Structure

```python
{
    'therapeutic_area': 'GLP1',
    'total_approvals': 12,
    'approvals_by_year': {
        2016: 3,
        2017: 2,
        2019: 1,
        # ...
    },
    'drugs_by_year': {
        2016: [
            {
                'brand_name': 'OZEMPIC',
                'generic_name': 'SEMAGLUTIDE',
                'manufacturer': 'Novo Nordisk',
                'approval_date': '20171205',
                'approval_year': 2017,
                'application_number': 'NDA209637'
            },
            # ...
        ]
    },
    'average_per_year': 1.2,
    'trend': 'decreasing',
    'summary': '...',
    'all_approvals': [...]
}
```

## Technical Implementation

### FDA Submissions Parsing

The skill extracts approval dates from the FDA `submissions` array:

1. **Primary Method**: Finds original approval submission (`submission_type='ORIG'` and `submission_status='AP'`)
2. **Fallback**: If no ORIG submission found, uses earliest approved submission
3. **Date Format**: Parses `submission_status_date` in YYYYMMDD format

### Trend Analysis Algorithm

```python
# Compare first half vs second half of approval years
first_half_avg = sum(approvals[:mid_point]) / mid_point
second_half_avg = sum(approvals[mid_point:]) / (len - mid_point)

if second_half_avg > first_half_avg * 1.2:
    trend = "increasing"
elif second_half_avg < first_half_avg * 0.8:
    trend = "decreasing"
else:
    trend = "stable"
```

## Example Results

### GLP-1 Approvals (2015-2024)

- **Total Approvals**: 12 drugs
- **Average per Year**: 1.2 approvals/year
- **Trend**: DECREASING (peaked in 2016 with 3 approvals)

**Timeline Visualization**:
```
Year   Count  Bar
----------------------------------------------------------------------
2015   0
2016   3      ██████████████████████████████████████████████████
2017   2      █████████████████████████████████
2018   0
2019   1      ████████████████
2020   1      ████████████████
2021   1      ████████████████
2022   1      ████████████████
2023   1      ████████████████
2024   2      █████████████████████████████████
```

**Complete Timeline**:
- 2015: 0 approvals
- 2016: 3 approvals (XULTOPHY 100/3.6, SOLIQUA 100/33, lixisenatide)
- 2017: 2 approvals (OZEMPIC, exenatide)
- 2018: 0 approvals
- 2019: 1 approval (RYBELSUS - oral semaglutide)
- 2020: 1 approval (semaglutide)
- 2021: 1 approval (WEGOVY - obesity)
- 2022: 1 approval (MOUNJARO - tirzepatide diabetes)
- 2023: 1 approval (ZEPBOUND - tirzepatide obesity)
- 2024: 2 approvals (liraglutide, exenatide)

## Business Applications

1. **Pipeline Gap Analysis**: Identify therapeutic areas with declining approvals → prioritize R&D investment
2. **Regulatory Timeline Forecasting**: Historical approval rates inform development timelines
3. **Competitive Intelligence**: Track competitor approval activity and market entry timing
4. **Portfolio Planning**: Allocate resources to therapeutic areas with increasing approval trends
5. **M&A Strategy**: Target companies in therapeutic areas with strong approval momentum

## Limitations

- **Drugs only, not biologics**: Searches FDA's Drugs@FDA database (NDAs). Does NOT include biologics approved under BLAs (e.g., CAR-T therapies, monoclonal antibodies, vaccines)
- Requires pre-defined drug lists or user-provided drug names (FDA API doesn't have clean indication/disease fields)
- Limited to 20 detail queries per drug to avoid token overflow
- Approval dates based on submission data (may not reflect final market approval in all cases)
- Some drugs may have multiple approvals (different indications) - skill captures all within time range

**What's covered**: Small molecule drugs, insulin products, traditional pharmaceuticals
**What's NOT covered**: CAR-T therapies, biologics, gene therapies, most cancer immunotherapies

## Related Skills

- `glp1-fda-drugs` - Get all FDA approved GLP-1 drugs with full details
- `company-fda-device-approvals` - FDA device approval timelines by company
- `diabetes-drugs-stopped-safety` - Drugs discontinued due to safety issues

## Data Source

- **MCP Server**: fda_mcp
- **Endpoint**: `lookup_drug` with `search_type='general'`
- **Database**: FDA Drugs@FDA database via openFDA API
- **Update Frequency**: Real-time (FDA data updated continuously)
