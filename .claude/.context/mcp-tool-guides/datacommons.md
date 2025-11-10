# Data Commons (mcp__datacommons-mcp)

## When to use
- Population statistics (demographics, prevalence)
- Disease burden data (DALY, mortality rates)
- Healthcare infrastructure (hospitals, facilities)
- Epidemiology for market sizing

## Methods
```json
{
  "method": "search_indicators",    // Find statistical variables
  "method": "get_observations"      // Get data values
}
```

## Parameter patterns

### Search for indicators
```json
{
  "method": "search_indicators",
  "query": "diabetes prevalence",
  "places": ["United States"],
  "per_search_limit": 10
}
```

### Get observations
```json
{
  "method": "get_observations",
  "variable_dcid": "Count_Person_Diabetes",
  "place_dcid": "country/USA",
  "date": "latest"
}
```

## Key response fields
- `variables[].dcid` - Variable identifier
- `variables[].places_with_data` - Places with data
- `dcid_name_mappings` - Readable names
- `place_observations[].time_series` - Data values over time

## Optimization rules
- Use `search_indicators` first to find variable DCIDs
- Then use `get_observations` with specific variable_dcid
- Qualify place names: "California, USA" not just "California"
- Use `date="latest"` for most recent data
