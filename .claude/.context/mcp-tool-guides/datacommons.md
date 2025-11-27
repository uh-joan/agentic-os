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

## CRITICAL: Two Different Place Identifiers

Data Commons uses **two different place identifier systems**. Mixing them is the #1 cause of bugs:

### 1. Place NAMES (for search_indicators)
Use **human-readable, qualified place names**:
- ✅ "United States" (full name, not "USA")
- ✅ "California, USA" (qualified with country)
- ✅ "New York City, USA" (qualified, city vs state)
- ❌ "USA" (too ambiguous)
- ❌ "California" (needs qualification)
- ❌ "country/USA" (this is a DCID, won't work here)

### 2. Place DCIDs (for get_observations)
Use **DCIDs returned from search_indicators**:
- ✅ "country/USA" (from places_with_data)
- ✅ "geoId/06" (from places_with_data)
- ❌ "United States" (human name won't work here)
- ❌ Hardcoded DCIDs (always get from search results)

## Two-Step Workflow (REQUIRED)

**Step 1: Search** - Find variable and place DCIDs
```python
result = search_indicators(
    query="diabetes prevalence",
    places=["United States"],        # Human-readable NAMES
    include_topics=False,
    per_search_limit=5
)

variable_dcid = result['variables'][0]['dcid']
place_dcid = result['variables'][0]['places_with_data'][0]  # Get DCID here!
```

**Step 2: Get Data** - Use DCIDs from Step 1
```python
obs = get_observations(
    variable_dcid=variable_dcid,     # From search results
    place_dcid=place_dcid,           # From search results (NOT hardcoded!)
    date="latest"
)
```

## Parameter patterns

### Search for indicators
```json
{
  "method": "search_indicators",
  "query": "diabetes prevalence",
  "places": ["United States", "China", "India"],
  "include_topics": false,
  "per_search_limit": 5
}
```

**Key Response Fields**:
```python
{
  'variables': [
    {
      'dcid': 'Count_Person_Diabetes',
      'places_with_data': ['country/USA', 'country/CHN', 'country/IND']
    }
  ],
  'dcid_name_mappings': {
    'Count_Person_Diabetes': 'Count of people with diabetes',
    'country/USA': 'United States',
    'country/CHN': 'China'
  }
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

**Key Response Fields**:
```python
{
  'place_observations': [
    {
      'place': {'dcid': 'country/USA', 'name': 'United States'},
      'time_series': [
        ('2020', 37100000),
        ('2021', 38200000)
      ]
    }
  ],
  'source_metadata': {'import_name': 'CDC_BRFSS'}
}
```

## Common Mistakes

❌ **Using short names in search_indicators**:
```python
places=["USA", "CA"]  # WRONG - too ambiguous
```

✅ **Use qualified full names**:
```python
places=["United States", "California, USA"]  # CORRECT
```

❌ **Hardcoding place_dcid in get_observations**:
```python
place_dcid="country/USA"  # WRONG - brittle, might not match variable
```

✅ **Get place_dcid from search results**:
```python
place_dcid = result['variables'][0]['places_with_data'][0]  # CORRECT
```

## Reference Implementation

See `.claude/skills/california-population/scripts/get_california_population.py` for complete working example following this pattern.
