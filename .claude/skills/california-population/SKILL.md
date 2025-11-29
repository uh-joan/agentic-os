---
name: get_california_population_time_series
description: >
  Retrieves California population time series from Data Commons using proper two-step workflow
  (search_indicators → get_observations). Returns historical data with year-over-year growth rates
  and comprehensive trend analysis. Demonstrates correct Data Commons API usage patterns.
category: population-epidemiology
mcp_servers:
  - datacommons_mcp
patterns:
  - datacommons_two_step_workflow
  - time_series_analysis
  - growth_rate_calculation
data_scope:
  total_results: Variable (all available years)
  geographical: California, USA
  temporal: All historical data
created: 2025-11-22
updated: 2025-11-27
complexity: medium
execution_time: ~2 seconds
migration_status: "Migrated to Data Commons v2 API (search_indicators + get_observations)"
---
# get_california_population_time_series


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What's the disease burden for california population?`
2. `@agent-pharma-search-specialist Show me prevalence data for california population`
3. `@agent-pharma-search-specialist Get epidemiology statistics for california population`


California population time series with growth trend analysis from Data Commons.

## API Pattern

Demonstrates the correct Data Commons two-step workflow:

1. **search_indicators()** - Find population variable for California
2. **get_observations()** - Retrieve all historical data

## Returns

```python
{
    'summary': {
        'total_years': int,
        'earliest_year': str,
        'latest_year': str,
        'earliest_population': int,
        'latest_population': int
    },
    'observations': [
        {
            'date': str,
            'population': int,
            'growth_rate': float  # Year-over-year % (from 2nd year onward)
        }
    ],
    'source': str  # Data source name
}
```