---
name: get_disease_burden_per_capita
description: >
  Calculate true disease burden per capita by combining WHO health indicators with Data Commons
  population data. Demonstrates multi-server integration with intelligent per-capita rate calculation.
  Handles both raw counts (e.g., death counts) and pre-calculated rates (e.g., mortality per 100k).
category: epidemiology
mcp_servers:
  - who_mcp
  - datacommons_mcp
patterns:
  - multi_server_query
  - datacommons_two_step_workflow
  - who_two_step_workflow
  - cli_arguments
  - generic_parameterization
  - per_capita_calculation
data_scope:
  total_results: Variable (by country and indicator)
  geographical: Global (32 countries mapped)
  temporal: Latest available from both WHO and Data Commons
created: 2025-11-22
updated: 2025-11-27
complexity: medium
execution_time: ~5-8 seconds
token_efficiency: 98%
cli_enabled: true
is_generic: true
status: "Multi-server integration working (WHO + Data Commons)"
version: "2.0"
---
# get_disease_burden_per_capita


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What's the disease burden for disease burden per capita?`
2. `@agent-pharma-search-specialist Show me prevalence data for disease burden per capita`
3. `@agent-pharma-search-specialist Get epidemiology statistics for disease burden per capita`


Calculate true disease burden per capita by combining WHO health indicator data with Data Commons population statistics.

## Features

✅ **Multi-server integration** - Combines WHO health data with Data Commons population data
✅ **Intelligent rate detection** - Automatically detects if indicator is already per-capita
✅ **True per-capita calculation** - Calculates rates per 100,000 population for raw counts
✅ **32 countries supported** - Full ISO3 to country name mapping for major countries
✅ **Graceful fallback** - Returns raw WHO data if population unavailable
✅ **Generic & reusable** - Works with any WHO health indicator keyword

## CLI Usage

```bash
# Diabetes prevalence in USA
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-burden-per-capita/scripts/get_disease_burden_per_capita.py USA "diabetes"

# Tuberculosis in India
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-burden-per-capita/scripts/get_disease_burden_per_capita.py IND "tuberculosis"

# Maternal mortality in Brazil
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-burden-per-capita/scripts/get_disease_burden_per_capita.py BRA "maternal mortality"

# Life expectancy in China
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-burden-per-capita/scripts/get_disease_burden_per_capita.py CHN "life expectancy"
```

## Parameters

- **country_code** (str, required): ISO 3-letter country code (e.g., USA, IND, CHN, BRA, GBR, DEU)
- **disease_indicator** (str, required): WHO health indicator keywords (e.g., "diabetes", "tuberculosis", "maternal mortality", "life expectancy")

## Supported Countries (32)

USA, IND, CHN, BRA, GBR, DEU, FRA, ITA, ESP, CAN, AUS, JPN, MEX, RUS, ZAF, KOR, IDN, TUR, SAU, NGA, EGY, PAK, BGD, VNM, THA, PHL, POL, ARG, NLD, BEL, SWE, CHE

## Returns

Dictionary containing:
- `success`: Boolean indicating if data retrieval succeeded
- `country`: ISO3 country code
- `indicator_name`: Full WHO indicator name
- `indicator_code`: WHO indicator code
- `raw_value`: Raw value from WHO
- `year`: Data year
- `population`: Population from Data Commons (if available)
- `per_100k_population`: Calculated per-capita rate (if population available)
- `is_already_rate`: Boolean indicating if indicator is pre-calculated rate
- `summary`: Human-readable formatted summary

## Example Output

```
=== Disease Burden Per Capita Analysis: USA ===

Indicator: Prevalence of obesity among adults, BMI &GreaterEqual; 30 (age-standardized estimate) (%)
Code: NCD_BMI_30A
Year: 2022

Raw Value: 36,500,000
Population: 340,110,988
Per 100,000 Population: 10,727.89

Calculation: Calculated as (36,500,000 / 340,110,988) × 100,000

Data Sources:
  - Disease/Health Data: WHO (World Health Organization)
  - Population Data: Data Commons (via Google/US Census)
```

## Implementation Details

### Multi-Server Workflow

1. **WHO MCP**: Search for health indicator by keyword → Get country-specific data
2. **Data Commons MCP**: Search for population indicator → Get latest population
3. **Per-Capita Calculation**:
   - If indicator is already a rate → use as-is
   - If indicator is a raw count → calculate (count / population) × 100,000

### Intelligent Rate Detection

The skill automatically detects if a WHO indicator is already expressed as a per-capita rate by checking for keywords like:
- "per 100"
- "per capita"
- "rate per"
- "/ 100"

For already-calculated rates, the raw value is returned without recalculation.

### Graceful Degradation

If Data Commons population data is unavailable for a country, the skill falls back to returning raw WHO indicator values with a clear note explaining the limitation.

## Version History

- **v2.0** (2025-11-27): Added Data Commons integration, true per-capita calculations, 32-country support
- **v1.0** (2025-11-22): Initial WHO-only version

## Related Skills

- `cvd-burden-per-capita`: Specialized CVD per-capita analysis (multi-country comparison)
- `get_california_population`: Data Commons population retrieval example
- `get_cvd_disease_burden`: WHO disease burden aggregation

## Data Sources

- **WHO MCP**: World Health Organization statistical database (GHO - Global Health Observatory)
- **Data Commons MCP**: Google/US Census Bureau population statistics