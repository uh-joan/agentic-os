---
name: get_breakthrough_therapy_designations_2024
description: >
  Retrieves FDA drug approvals from 2024 and identifies breakthrough therapy
  designations where available in the API. Provides drug name, indication,
  approval date, sponsor, and mechanism of action.

  IMPORTANT: The FDA drug labels API may not contain complete breakthrough
  designation data. For authoritative breakthrough therapy designation lists,
  consult FDA's official breakthrough therapy webpage or drug approval
  announcements.

  Use this skill when analyzing:
  - Fast-track regulatory strategies
  - Competitive intelligence for 2024 approvals
  - Novel mechanisms of action in recent approvals
  - Rare disease drug development trends

  Keywords: breakthrough therapy, FDA approval, 2024, fast track, priority review,
  regulatory strategy, competitive intelligence, novel drugs
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - data_filtering
  - temporal_query
data_scope:
  total_results: 7
  geographical: United States
  temporal: 2024 calendar year
  coverage: FDA-approved drugs with 2024 marketing status dates
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw FDA JSON
---

# get_breakthrough_therapy_designations_2024

## Purpose

Retrieves all FDA drug approvals from 2024 and identifies breakthrough therapy designations where this information is available in the FDA drug labels API.

Breakthrough therapy designation is granted by FDA to accelerate development and review of drugs for serious or life-threatening conditions that demonstrate substantial improvement over existing therapies.

## Usage

**When to use this skill**:
- Analyzing fast-track regulatory strategies for 2024
- Competitive intelligence on novel drug approvals
- Understanding recent therapeutic innovations
- Identifying emerging mechanisms of action
- Tracking rare disease drug development

**Example queries**:
- "What drugs got breakthrough designation in 2024?"
- "List FDA approvals from 2024"
- "Show me recent breakthrough therapies"

## Data Sources

- **FDA Drug Labels API**: Primary source for approval dates and drug information
- **Search Strategy**: Filters drugs by 2024 marketing status dates
- **Limitation**: Breakthrough designation status may not be fully captured in API structured fields

## Implementation Details

### Search Strategy

1. Queries FDA drug labels database for broad sample (limit: 100)
2. Filters results by `marketing_status_date` containing "2024"
3. Extracts drug information from `openfda` fields
4. Checks `submissions` array for breakthrough designation indicators

### Data Extracted

For each 2024 approval:
- **Brand name**: Commercial product name
- **Generic name**: Active ingredient name
- **Application number**: NDA/BLA number
- **Sponsor**: Pharmaceutical company
- **Approval date**: Marketing status date
- **Indication**: Therapeutic use
- **Mechanism**: Mechanism of action (MoA)
- **Breakthrough status**: If found in submission data

### Known Limitations

1. **Incomplete Breakthrough Data**: FDA drug labels API does not consistently include breakthrough designation in structured fields
2. **Sample Size**: Default query retrieves 100-drug sample; may not capture all 2024 approvals
3. **Verification Needed**: For authoritative breakthrough designation list, consult:
   - FDA Breakthrough Therapy Designations webpage
   - FDA drug approval press releases
   - CenterWatch or FDA RSS feeds

## Output Format

Returns dictionary with:
```python
{
    'total_count': int,           # Total 2024 approvals found
    'breakthrough_count': int,    # Confirmed breakthrough designations in API
    'drugs': [                    # List of drug information dictionaries
        {
            'brand_name': str,
            'generic_name': str,
            'application_number': str,
            'sponsor': str,
            'approval_date': str,
            'indication': str,
            'mechanism': str,
            'breakthrough_designated': bool,
            'submission_info': str
        }
    ],
    'summary': str                # Formatted summary table
}
```

## Example Output

```
================================================================================
FDA DRUG APPROVALS IN 2024 - BREAKTHROUGH THERAPY STATUS
================================================================================

Total 2024 approvals found in sample: 7
Confirmed breakthrough therapy designations in API: 0

Brand Name                Generic Name                   Date         BT
------------------------- ------------------------------ ------------ ----
WINREVAIR                 sotatercept-csrk               2024-03-26   No
XOLREMDI                  mavorixafor                    2024-04-17   No
REZDIFFRA                 resmetirom                     2024-03-14   No
...
```

## Business Value

- **Regulatory Strategy**: Identify fast-track pathways and precedents
- **Competitive Intelligence**: Track competitor approvals and novel mechanisms
- **Market Timing**: Understand approval trends and therapeutic areas
- **Partnership Opportunities**: Find innovative companies with recent approvals
- **Clinical Development**: Learn from successful regulatory strategies

## Maintenance Notes

- API search may need periodic adjustment to capture all 2024 approvals
- Consider supplementing with FDA announcements for complete breakthrough designation data
- Monitor FDA API changes to submission data structure
