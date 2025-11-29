---
name: get_cvd_burden_per_capita
description: >
  Calculate cardiovascular disease burden per capita by combining WHO mortality data
  with Data Commons population statistics. Analyzes 15 countries, deaths per 100k.
  Uses proper Data Commons two-step workflow (search_indicators → get_observations).
category: epidemiology
mcp_servers:
  - who_mcp
  - datacommons_mcp
patterns:
  - multi_server_query
  - datacommons_two_step_workflow
  - data_normalization
  - error_handling
data_scope:
  total_countries: 15
  geographical: Global
  temporal: Most recent
created: 2025-11-22
updated: 2025-11-27
complexity: medium
execution_time: ~5 seconds
token_efficiency: 99%
migration_status: "Migrated to Data Commons v2 API (search_indicators + get_observations)"
---
# get_cvd_burden_per_capita


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What's the disease burden for cardiovascular disease?`
2. `@agent-pharma-search-specialist Show me prevalence data for cardiovascular disease`
3. `@agent-pharma-search-specialist Get epidemiology statistics for cardiovascular disease`


CVD mortality burden per capita analysis combining WHO and Data Commons data.

## API Pattern

Combines data from two MCP servers:
1. **WHO MCP** - CVD mortality data
2. **Data Commons MCP** - Population data (using two-step workflow)

## Helper Function

`get_population_data(country_name)` - Internal helper that wraps the Data Commons two-step workflow:
- search_indicators() to find population variable
- get_observations() to retrieve latest population

## Returns

```python
{
    'cvd_burden_data': [
        {
            'country': str,
            'cvd_deaths': int,
            'population': int,
            'deaths_per_100k': float
        }
    ],
    'summary': {
        'countries_with_complete_data': int,
        'average_burden_per_100k': float,
        'highest_burden': {'country': str, 'rate': float},
        'lowest_burden': {'country': str, 'rate': float}
    },
    'data_availability': {
        'total_countries': int,
        'who_success': int,
        'dc_success': int,
        'both_success': int
    }
}
```