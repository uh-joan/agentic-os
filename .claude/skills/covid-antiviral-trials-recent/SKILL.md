---
name: get_covid_antiviral_trials_recent
description: >
  Monitor COVID-19 antiviral clinical trials that started recruiting recently.
  Focuses on antiviral treatments (excludes vaccines). Filters for RECRUITING
  or NOT_YET_RECRUITING status. Provides breakdown by sponsor, phase, and
  geographic location. Useful for tracking emerging COVID-19 therapeutic
  development activity, competitive intelligence in antiviral space, and
  monitoring trial starts in specific time windows.

  Keywords: COVID-19, SARS-CoV-2, antiviral, recent trials, recruiting,
  pandemic therapeutics, emerging trials
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - date_filtering
  - status_aggregation
data_scope:
  total_results: Varies (2-50 depending on pandemic activity)
  geographical: Global
  temporal: Last 30 days (configurable)
created: 2025-11-23
last_updated: 2025-11-23
complexity: medium
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_covid_antiviral_trials_recent

## Purpose
Monitors COVID-19 antiviral clinical trials that have recently started recruiting. Excludes vaccine trials to focus on therapeutic interventions. Provides comprehensive breakdown of sponsors, phases, and geographic distribution.

## Usage
Use this skill when you need to:
- Track emerging COVID-19 antiviral trial activity
- Monitor competitive landscape in COVID therapeutics
- Identify recent trial starts for specific time windows
- Analyze sponsor activity in COVID-19 antiviral space
- Find recruiting opportunities in specific therapeutic areas

## Trigger Keywords
- "COVID-19 antiviral trials"
- "Recent COVID trials"
- "New antiviral studies"
- "SARS-CoV-2 therapeutics"
- "COVID treatment trials recruiting"

## Implementation Details

**Data Source**: ClinicalTrials.gov via MCP

**Filters Applied**:
- Query: "(COVID-19 OR SARS-CoV-2) AND antiviral"
- Status: RECRUITING or NOT_YET_RECRUITING
- Date: Started recruiting in last N days (default 30)
- Post-filtering: Excludes trials with "vaccine" in title

**Data Extracted**:
- NCT ID
- Trial title
- Sponsor company
- Recruitment status
- Start date
- Intervention/drug name
- Geographic locations
- Enrollment targets
- Study phase

**Pagination**: Full implementation with pageToken handling

**Return Format**:
```python
{
    'total_count': int,
    'data': [
        {
            'nct_id': str,
            'title': str,
            'sponsor': str,
            'status': str,
            'start_date': str,
            'intervention': str,
            'locations': str,
            'enrollment': str,
            'phase': str
        },
        ...
    ],
    'summary': {
        'total_trials': int,
        'search_criteria': str,
        'note': str,
        'top_sponsors': dict,
        'phase_breakdown': dict,
        'top_locations': dict,
        'pages_fetched': int
    }
}
```

## Notes
- COVID-19 trial activity has significantly decreased since pandemic peak
- May return 0 results during periods of low activity
- Consider broadening date range if no recent trials found
- Start dates may be estimated or actual depending on trial reporting
- Location parsing is basic pattern matching - may not capture all countries
