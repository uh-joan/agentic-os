# WHO Global Health Observatory MCP Server - Complete API Guide

**Server**: `who-mcp-server`
**Tool**: `who-health`
**Data Source**: WHO Global Health Observatory (GHO) via modern OData API
**Response Format**: JSON (OData format with `value` arrays)

---

## 🔴 CRITICAL ODATA QUERY PATTERNS

### 1. Two-Step Workflow (Search → Query)
```python
# ✅ CORRECT: Search for indicators first
results = search_indicators(keywords="life expectancy")
indicator_code = results['indicators'][0]['code']  # "WHOSIS_000001"

# Then query data with exact code
data = get_health_data(indicator_code="WHOSIS_000001")

# ❌ WRONG: Don't guess indicator codes
data = get_health_data(indicator_code="life_expectancy")  # Invalid code
```

### 2. OData Filter Syntax (Standard Protocol)
```python
# ✅ CORRECT: Standard OData operators
filter="SpatialDim eq 'USA' and TimeDim eq 2020"
filter="TimeDim ge 2015 and TimeDim le 2020"
filter="Dim1 eq 'MLE'"
filter="Dim1 ne null"

# ❌ WRONG: Non-standard syntax
filter="country='USA'"        # Use SpatialDim, not country
filter="year>=2015"           # Use 'ge', not '>='
filter="sex=='male'"          # Use Dim1 eq 'MLE'
```

### 3. Dimension Codes (WHO-Specific)
```python
# ✅ CORRECT: WHO dimension codes
# Sex: MLE (male), FMLE (female), BTSX (both sexes)
# Regions: AFR, AMR, SEAR, EUR, EMR, WPR
# Countries: ISO 3-letter codes (USA, GBR, CHN)

filter="Dim1 eq 'MLE'"           # Male data
region_code="EUR"                # European Region

# ❌ WRONG: Generic terms
filter="sex eq 'male'"           # Use 'MLE'
region_code="Europe"             # Use 'EUR'
country_code="US"                # Use 'USA' (3 letters)
```

### 4. Disaggregation Handling
```python
# ✅ CORRECT: Check for sex-disaggregated data
filter="SpatialDim eq 'USA' and Dim1 ne null"  # Has sex breakdown
filter="Dim1 eq null"                           # Only total/both sexes

# Get all disaggregation types
sex_data = get_health_data(
    indicator_code="WHOSIS_000001",
    filter="SpatialDim eq 'USA' and TimeDim eq 2020 and Dim1 ne null"
)

# ❌ WRONG: Assume disaggregation exists
# Not all indicators have sex breakdowns - check first
```

---

## Quick Reference

### Available Methods (6 total)

| Method | Purpose | Common Use |
|--------|---------|------------|
| `get_dimensions` | List all data dimensions | Discover available dimensions |
| `get_dimension_codes` | Get codes for a dimension | Country codes, WHO regions, years |
| `search_indicators` | Find health indicators | Natural language search |
| `get_health_data` | Raw data with OData filters | Advanced queries, time series |
| `get_country_data` | Country/region-specific data | Simplified country queries |
| `get_cross_table` | Tabular cross-country view | Multi-country comparisons |

### Common Indicator Codes

| Code | Indicator | Category |
|------|-----------|----------|
| `WHOSIS_000001` | Life expectancy at birth | Mortality |
| `MDG_0000000001` | Maternal mortality ratio | Maternal health |
| `GHED_CHE_pc_PPP_INT` | Health expenditure per capita | Health systems |
| `M_Est_smk_curr_std` | Smoking prevalence | Risk factors |
| `SA_0000001688` | Suicide mortality rate | Mental health |
| `WHS9_86` | Infant mortality rate | Child health |
| `WHS3_48` | Tuberculosis incidence | Infectious diseases |

### OData Filter Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equals | `SpatialDim eq 'USA'` |
| `ne` | Not equals | `Dim1 ne null` |
| `ge` | Greater or equal | `TimeDim ge 2015` |
| `le` | Less or equal | `TimeDim le 2020` |
| `and` | Logical AND | `SpatialDim eq 'USA' and TimeDim eq 2020` |
| `or` | Logical OR | `SpatialDim eq 'USA' or SpatialDim eq 'GBR'` |
| `date()` | Date function | `date(TimeDimensionBegin) ge 2011-01-01` |

### WHO Region Codes

| Code | Region | Countries Example |
|------|--------|-------------------|
| `AFR` | African Region | Nigeria, South Africa, Kenya |
| `AMR` | Region of the Americas | USA, Brazil, Canada, Mexico |
| `SEAR` | South-East Asia Region | India, Indonesia, Thailand |
| `EUR` | European Region | Germany, France, UK, Russia |
| `EMR` | Eastern Mediterranean | Egypt, Saudi Arabia, Pakistan |
| `WPR` | Western Pacific Region | China, Japan, Australia |

### Sex Disaggregation Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `MLE` | Male | `Dim1 eq 'MLE'` |
| `FMLE` | Female | `Dim1 eq 'FMLE'` |
| `BTSX` | Both sexes | `Dim1 eq 'BTSX'` |
| `null` | No disaggregation | `Dim1 eq null` |

---

## Method 1: `get_dimensions`

**Purpose**: List all available data dimensions in WHO database

**Parameters**: None

**Returns**: List of dimension codes (COUNTRY, REGION, YEAR, SEX, etc.)

**Token Usage**: ~100-200 tokens

**Use When**:
- Starting WHO data exploration
- Discovering available dimension types
- Understanding data structure

### Response Structure
```json
{
  "dimensions": [
    {
      "code": "COUNTRY",
      "label": "Country"
    },
    {
      "code": "REGION",
      "label": "WHO Region"
    },
    {
      "code": "YEAR",
      "label": "Year"
    }
  ]
}
```

### Code Examples

#### Example 1: List All Dimensions
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_dimensions

# Get all dimensions
dims = get_dimensions()

print("Available WHO Data Dimensions:")
print("-" * 40)

for dim in dims.get('dimensions', []):
    code = dim.get('code')
    label = dim.get('label')
    print(f"{code:15s} {label}")

# Output:
# COUNTRY         Country
# REGION          WHO Region
# YEAR            Year
# SEX             Sex
```

---

## Method 2: `get_dimension_codes`

**Purpose**: Get codes and labels for a specific dimension

**Parameters**:
- `dimension_code` (required): Dimension to retrieve
  - Common values: `"COUNTRY"`, `"REGION"`, `"YEAR"`, `"SEX"`

**Returns**: Codes and labels for the specified dimension

**Token Usage**:
- COUNTRY: ~8,000 tokens (194 countries)
- REGION: ~200 tokens (6 regions)
- YEAR: ~500 tokens (varies by indicator)
- SEX: ~100 tokens (3-4 codes)

**Use When**:
- Need valid country codes for filtering
- Building dropdown lists for UI
- Validating dimension values before querying

### Response Structure
```json
{
  "dimension": "COUNTRY",
  "codes": [
    {
      "code": "USA",
      "label": "United States of America"
    },
    {
      "code": "GBR",
      "label": "United Kingdom"
    }
  ]
}
```

### Code Examples

#### Example 1: Get All Country Codes
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_dimension_codes

# Get all countries
countries = get_dimension_codes(dimension_code="COUNTRY")

print(f"Total countries: {len(countries.get('codes', []))}")
print("\nSample countries:")

for country in countries.get('codes', [])[:10]:
    code = country.get('code')
    label = country.get('label')
    print(f"{code}: {label}")

# Output:
# Total countries: 194
#
# Sample countries:
# AFG: Afghanistan
# ALB: Albania
# DZA: Algeria
# AND: Andorra
# AGO: Angola
```

#### Example 2: Get WHO Regions
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_dimension_codes

# Get WHO regions
regions = get_dimension_codes(dimension_code="REGION")

print("WHO Regions:")
print("-" * 60)

for region in regions.get('codes', []):
    code = region.get('code')
    label = region.get('label')
    print(f"{code:5s} {label}")

# Output:
# WHO Regions:
# ------------------------------------------------------------
# AFR   African Region
# AMR   Region of the Americas
# SEAR  South-East Asia Region
# EUR   European Region
# EMR   Eastern Mediterranean Region
# WPR   Western Pacific Region
```

#### Example 3: Get Sex Disaggregation Codes
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_dimension_codes

# Get sex codes
sex_codes = get_dimension_codes(dimension_code="SEX")

sex_mapping = {}
for sex in sex_codes.get('codes', []):
    code = sex.get('code')
    label = sex.get('label')
    sex_mapping[code] = label
    print(f"{code}: {label}")

# Output:
# MLE: Male
# FMLE: Female
# BTSX: Both sexes

# Use in queries
print(f"\nQuery male data: Dim1 eq '{list(sex_mapping.keys())[0]}'")
```

---

## Method 3: `search_indicators`

**Purpose**: Find health indicators using keywords and natural language

**Parameters**:
- `keywords` (required): Search terms for health indicators
  - Examples: `"life expectancy"`, `"maternal mortality"`, `"HIV prevalence"`

**Returns**: Matching health indicators with codes and names

**Token Usage**: ~300-800 tokens (depends on result count)

**Use When**:
- Finding indicator codes for data queries
- Discovering available health data
- Natural language exploration

### Response Structure
```json
{
  "indicators": [
    {
      "code": "WHOSIS_000001",
      "name": "Life expectancy at birth (years)",
      "category": "",
      "definition": "",
      "method": "",
      "interpretation": ""
    },
    {
      "code": "WHOSIS_000015",
      "name": "Healthy life expectancy (HALE) at birth (years)",
      "category": "",
      "definition": "",
      "method": "",
      "interpretation": ""
    }
  ]
}
```

### Code Examples

#### Example 1: Search for Life Expectancy
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import search_indicators

# Search for indicators
results = search_indicators(keywords="life expectancy")

print(f"Found {len(results.get('indicators', []))} indicators")
print("\nLife Expectancy Indicators:")
print("-" * 80)

for indicator in results.get('indicators', []):
    code = indicator.get('code')
    name = indicator.get('name')
    print(f"{code:20s} {name}")

# Output:
# Found 3 indicators
#
# Life Expectancy Indicators:
# --------------------------------------------------------------------------------
# WHOSIS_000001        Life expectancy at birth (years)
# WHOSIS_000015        Healthy life expectancy (HALE) at birth (years)
# WHOSIS_000002        Life expectancy at age 60 (years)
```

#### Example 2: Search for Maternal Health
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import search_indicators

# Search maternal health
results = search_indicators(keywords="maternal mortality")

print("Maternal Health Indicators:")
for indicator in results.get('indicators', []):
    code = indicator.get('code')
    name = indicator.get('name')

    if 'ratio' in name.lower():
        print(f"✓ {code}: {name}")
        # Save for later query
        maternal_mortality_code = code

# Output:
# Maternal Health Indicators:
# ✓ MDG_0000000001: Maternal mortality ratio (per 100 000 live births)
```

#### Example 3: Multi-Step Discovery Workflow
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import search_indicators, get_health_data

# Step 1: Search for health expenditure indicators
results = search_indicators(keywords="health expenditure")

# Step 2: Filter for per capita indicators
per_capita_codes = []
for indicator in results.get('indicators', []):
    code = indicator.get('code')
    name = indicator.get('name')

    if 'capita' in name.lower():
        per_capita_codes.append(code)
        print(f"Found: {code} - {name}")

# Step 3: Query data with discovered code
if per_capita_codes:
    data = get_health_data(
        indicator_code=per_capita_codes[0],
        filter="SpatialDim eq 'USA' and TimeDim eq 2019",
        top=10
    )

    # Process results
    for record in data.get('value', []):
        value = record.get('NumericValue')
        print(f"\nUS Health Expenditure per Capita (2019): ${value:.2f}")
```

---

## Method 4: `get_health_data`

**Purpose**: Retrieve comprehensive health data with advanced OData filtering

**Parameters**:
- `indicator_code` (required): WHO health indicator code (e.g., `"WHOSIS_000001"`)
- `top` (optional): Maximum number of records to return (default: all)
- `filter` (optional): OData filter expression for advanced filtering

**Returns**: Raw health data records with all available fields

**Token Usage**:
- Without filter: ~500-5,000 tokens per 100 records (varies by indicator)
- With country filter: ~50-200 tokens per country-year
- With time range: ~100-500 tokens per country (depends on years)

**Use When**:
- Need advanced filtering capabilities
- Building time series analysis
- Multiple countries with complex logic
- Checking for disaggregation (sex, age groups)

### OData Filter Syntax

#### Basic Filtering
```python
# Single country, single year
filter="SpatialDim eq 'USA' and TimeDim eq 2020"

# Multiple conditions
filter="SpatialDim eq 'USA' and TimeDim eq 2020 and Dim1 eq 'MLE'"
```

#### Time Range Filtering
```python
# Year range
filter="TimeDim ge 2015 and TimeDim le 2020"

# Greater than
filter="TimeDim ge 2010"

# Date functions
filter="date(TimeDimensionBegin) ge 2011-01-01 and date(TimeDimensionBegin) lt 2012-01-01"
```

#### Disaggregation Filtering
```python
# Has sex breakdown
filter="Dim1 ne null"

# No disaggregation (totals only)
filter="Dim1 eq null"

# Specific sex
filter="Dim1 eq 'MLE'"  # Male only
```

### Response Structure
```json
{
  "value": [
    {
      "code": "WHOSIS_000001",
      "SpatialDim": "USA",
      "TimeDim": 2020,
      "Dim1": "BTSX",
      "NumericValue": 78.93,
      "Low": 78.5,
      "High": 79.3,
      "Comments": ""
    }
  ]
}
```

### Code Examples

#### Example 1: Basic Country Query
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_health_data

# Get US life expectancy for 2020
data = get_health_data(
    indicator_code="WHOSIS_000001",
    filter="SpatialDim eq 'USA' and TimeDim eq 2020"
)

for record in data.get('value', []):
    country = record.get('SpatialDim')
    year = record.get('TimeDim')
    value = record.get('NumericValue')
    low = record.get('Low')
    high = record.get('High')

    print(f"{country} Life Expectancy ({year}):")
    print(f"  Value: {value:.2f} years")
    print(f"  Range: {low:.2f} - {high:.2f} years")

# Output:
# USA Life Expectancy (2020):
#   Value: 78.93 years
#   Range: 78.50 - 79.30 years
```

#### Example 2: Time Series Analysis
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_health_data

# Get 10-year trend
data = get_health_data(
    indicator_code="WHOSIS_000001",
    filter="SpatialDim eq 'USA' and TimeDim ge 2010 and TimeDim le 2020"
)

# Build time series
time_series = []
for record in data.get('value', []):
    year = record.get('TimeDim')
    value = record.get('NumericValue')
    if year and value:
        time_series.append((year, value))

# Sort and analyze
time_series.sort()

print("US Life Expectancy Trend (2010-2020):")
print("-" * 40)

for year, value in time_series:
    print(f"{year}: {value:.2f} years")

# Calculate change
if len(time_series) >= 2:
    start_year, start_value = time_series[0]
    end_year, end_value = time_series[-1]
    change = end_value - start_value

    print(f"\nChange ({start_year}-{end_year}): {change:+.2f} years")

# Output:
# US Life Expectancy Trend (2010-2020):
# ----------------------------------------
# 2010: 78.54 years
# 2011: 78.64 years
# ...
# 2020: 77.28 years
#
# Change (2010-2020): -1.26 years
```

#### Example 3: Sex-Disaggregated Data
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_health_data

# Get sex-disaggregated data
data = get_health_data(
    indicator_code="WHOSIS_000001",
    filter="SpatialDim eq 'USA' and TimeDim eq 2020 and Dim1 ne null"
)

sex_labels = {
    'MLE': 'Male',
    'FMLE': 'Female',
    'BTSX': 'Both sexes'
}

sex_data = {}
for record in data.get('value', []):
    sex = record.get('Dim1')
    value = record.get('NumericValue')
    if sex and value:
        sex_data[sex] = value

print("US Life Expectancy by Sex (2020):")
print("-" * 40)

for code, value in sorted(sex_data.items()):
    label = sex_labels.get(code, code)
    print(f"{label:12s} {value:.2f} years")

# Calculate gender gap
if 'MLE' in sex_data and 'FMLE' in sex_data:
    gap = sex_data['FMLE'] - sex_data['MLE']
    print(f"\nGender gap: {gap:.2f} years (favoring {'females' if gap > 0 else 'males'})")

# Output:
# US Life Expectancy by Sex (2020):
# ----------------------------------------
# Both sexes  78.93 years
# Female      81.10 years
# Male        76.30 years
#
# Gender gap: 4.80 years (favoring females)
```

#### Example 4: Multi-Country Comparison
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_health_data

# Get data for multiple countries
data = get_health_data(
    indicator_code="GHED_CHE_pc_PPP_INT",
    filter="TimeDim eq 2019",
    top=200
)

# Extract and rank by expenditure
countries = []
for record in data.get('value', []):
    country = record.get('SpatialDim')
    value = record.get('NumericValue')
    if value:
        countries.append((country, value))

countries.sort(key=lambda x: x[1], reverse=True)

print("Top 10 Health Expenditure per Capita (2019):")
print("-" * 50)

for rank, (country, value) in enumerate(countries[:10], 1):
    print(f"{rank:2d}. {country:5s} ${value:8,.0f}")

# Output:
# Top 10 Health Expenditure per Capita (2019):
# --------------------------------------------------
#  1. USA   $11,072
#  2. CHE   $9,674
#  3. NOR   $7,065
#  4. DEU   $6,646
#  5. SWE   $6,223
```

---

## Method 5: `get_country_data`

**Purpose**: Simplified interface for country/region-specific health data queries

**Parameters**:
- `indicator_code` (required): WHO health indicator code
- `country_code` (optional): ISO 3-letter country code (e.g., `"USA"`, `"GBR"`)
- `region_code` (optional): WHO region code (e.g., `"EUR"`, `"AMR"`)
- `year` (optional): Specific year or year range (e.g., `"2020"`, `"2015:2020"`)
- `sex` (optional): Sex dimension filter (`"MLE"`, `"FMLE"`, `"BTSX"`)
- `top` (optional): Maximum number of records

**Returns**: Country-specific health data

**Token Usage**:
- Single country-year: ~50-100 tokens
- Year range: ~100-500 tokens (depends on years)
- Regional query: ~500-2,000 tokens (depends on countries)

**Use When**:
- Simple country-specific queries
- Don't want to write OData filters
- Quick data retrieval for dashboards
- Regional analysis (all countries in region)

### Response Structure
```json
{
  "value": [
    {
      "code": "WHOSIS_000001",
      "SpatialDim": "USA",
      "TimeDim": 2020,
      "NumericValue": 78.93
    }
  ]
}
```

### Code Examples

#### Example 1: Simple Country Query
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

# Get US life expectancy for 2020
data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2020"
)

for record in data.get('value', []):
    value = record.get('NumericValue')
    print(f"US Life Expectancy (2020): {value:.2f} years")

# Output:
# US Life Expectancy (2020): 78.93 years
```

#### Example 2: Time Trend for Country
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

# Get 10-year trend
data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2010:2020"
)

# Extract time series
years = []
values = []
for record in data.get('value', []):
    year = record.get('TimeDim')
    value = record.get('NumericValue')
    if year and value:
        years.append(year)
        values.append(value)

# Calculate trend
if len(values) >= 2:
    change = values[-1] - values[0]
    years_span = years[-1] - years[0]
    annual_change = change / years_span

    print(f"US Life Expectancy Trend ({years[0]}-{years[-1]}):")
    print(f"  Start: {values[0]:.2f} years")
    print(f"  End: {values[-1]:.2f} years")
    print(f"  Total change: {change:+.2f} years")
    print(f"  Annual change: {annual_change:+.3f} years/year")

# Output:
# US Life Expectancy Trend (2010-2020):
#   Start: 78.54 years
#   End: 77.28 years
#   Total change: -1.26 years
#   Annual change: -0.126 years/year
```

#### Example 3: Regional Analysis (All Countries in Europe)
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

# Get all European countries data
data = get_country_data(
    indicator_code="WHOSIS_000001",
    region_code="EUR",
    year="2020",
    top=100
)

# Analyze regional distribution
values = []
countries = []

for record in data.get('value', []):
    country = record.get('SpatialDim')
    value = record.get('NumericValue')
    if value:
        values.append(value)
        countries.append((country, value))

if values:
    avg = sum(values) / len(values)
    min_val = min(values)
    max_val = max(values)

    print(f"European Region Life Expectancy (2020):")
    print(f"  Countries: {len(values)}")
    print(f"  Average: {avg:.2f} years")
    print(f"  Range: {min_val:.2f} - {max_val:.2f} years")

    # Find extremes
    countries.sort(key=lambda x: x[1])
    print(f"\n  Lowest: {countries[0][0]} ({countries[0][1]:.2f} years)")
    print(f"  Highest: {countries[-1][0]} ({countries[-1][1]:.2f} years)")

# Output:
# European Region Life Expectancy (2020):
#   Countries: 53
#   Average: 77.82 years
#   Range: 68.30 - 84.30 years
#
#   Lowest: UKR (68.30 years)
#   Highest: CHE (84.30 years)
```

#### Example 4: Gender Gap Analysis
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

# Get male data
male_data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2020",
    sex="MLE"
)

# Get female data
female_data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2020",
    sex="FMLE"
)

male_value = male_data.get('value', [{}])[0].get('NumericValue')
female_value = female_data.get('value', [{}])[0].get('NumericValue')

if male_value and female_value:
    gap = female_value - male_value
    gap_pct = (gap / male_value) * 100

    print("US Life Expectancy Gender Gap (2020):")
    print(f"  Male: {male_value:.2f} years")
    print(f"  Female: {female_value:.2f} years")
    print(f"  Gap: {gap:.2f} years ({gap_pct:.1f}%)")

# Output:
# US Life Expectancy Gender Gap (2020):
#   Male: 76.30 years
#   Female: 81.10 years
#   Gap: 4.80 years (6.3%)
```

---

## Method 6: `get_cross_table`

**Purpose**: Generate tabular views of health data across countries and time periods

**Parameters**:
- `indicator_code` (required): WHO health indicator code
- `countries` (optional): Comma-separated list of country codes (e.g., `"USA,GBR,CHN"`)
- `years` (optional): Year range (`"YYYY:YYYY"`) or specific year (`"YYYY"`)
- `sex` (optional): Sex dimension filter (`"MLE"`, `"FMLE"`, `"BTSX"`)

**Returns**: Structured table with countries as rows and years as columns

**Token Usage**: ~100-500 tokens per country-year combination

**Use When**:
- Cross-country comparisons needed
- Building reports or dashboards
- Time series visualization
- Multiple countries, multiple years

### Response Structure
```json
{
  "rows": [
    {
      "country": "USA",
      "2015": 78.69,
      "2016": 78.69,
      "2017": 78.54,
      "2018": 78.69,
      "2019": 78.79,
      "2020": 77.28
    },
    {
      "country": "GBR",
      "2015": 81.20,
      "2016": 81.20,
      "2017": 81.26,
      "2018": 81.26,
      "2019": 81.26,
      "2020": 80.40
    }
  ]
}
```

### Code Examples

#### Example 1: G7 Countries Comparison
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_cross_table

# Compare G7 countries
table = get_cross_table(
    indicator_code="WHOSIS_000001",
    countries="USA,GBR,JPN,DEU,FRA,ITA,CAN",
    years="2015:2020"
)

# Display as formatted table
print("Life Expectancy Comparison: G7 Countries (2015-2020)")
print("-" * 80)
print("Country", end="  ")
for year in range(2015, 2021):
    print(f"{year:>6d}", end="  ")
print()
print("-" * 80)

for row in table.get('rows', []):
    country = row.get('country')
    print(f"{country:7s}", end="  ")

    for year in range(2015, 2021):
        value = row.get(str(year))
        if value:
            print(f"{value:6.2f}", end="  ")
        else:
            print("   N/A", end="  ")
    print()

# Output:
# Life Expectancy Comparison: G7 Countries (2015-2020)
# --------------------------------------------------------------------------------
# Country    2015    2016    2017    2018    2019    2020
# --------------------------------------------------------------------------------
# USA        78.69   78.69   78.54   78.69   78.79   77.28
# GBR        81.20   81.20   81.26   81.26   81.26   80.40
# JPN        83.79   84.10   84.21   84.21   84.36   84.62
# DEU        80.84   81.07   81.07   81.00   81.11   81.33
# FRA        82.39   82.41   82.48   82.66   82.66   82.32
# ITA        82.77   82.98   83.06   83.11   83.24   82.29
# CAN        82.00   82.05   82.05   82.05   82.05   81.75
```

#### Example 2: BRICS Health Expenditure Growth
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_cross_table

# BRICS health expenditure
table = get_cross_table(
    indicator_code="GHED_CHE_pc_PPP_INT",
    countries="BRA,RUS,IND,CHN,ZAF",
    years="2010:2020"
)

print("BRICS Health Expenditure Growth (2010-2020)")
print("-" * 60)

for row in table.get('rows', []):
    country = row.get('country')
    start = row.get('2010')
    end = row.get('2020')

    if start and end:
        growth = ((end - start) / start) * 100
        print(f"{country:5s} ${start:7,.0f} → ${end:7,.0f}  ({growth:+6.1f}%)")

# Output:
# BRICS Health Expenditure Growth (2010-2020)
# ------------------------------------------------------------
# BRA   $1,234 → $1,564  (+26.7%)
# RUS   $  927 → $1,247  (+34.5%)
# IND   $  134 → $  267  (+99.3%)
# CHN   $  419 → $1,040  (+148.2%)
# ZAF   $  638 → $  748  (+17.2%)
```

#### Example 3: Ranking Countries (Single Year)
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_cross_table

# North American comparison
table = get_cross_table(
    indicator_code="WHOSIS_000001",
    countries="USA,MEX,CAN",
    years="2020"
)

# Rank by value
rankings = []
for row in table.get('rows', []):
    country = row.get('country')
    value = row.get('2020')
    if value:
        rankings.append((country, value))

rankings.sort(key=lambda x: x[1], reverse=True)

print("North American Life Expectancy Rankings (2020):")
print("-" * 50)

for rank, (country, value) in enumerate(rankings, 1):
    print(f"{rank}. {country}: {value:.2f} years")

# Output:
# North American Life Expectancy Rankings (2020):
# --------------------------------------------------
# 1. CAN: 81.75 years
# 2. USA: 77.28 years
# 3. MEX: 75.05 years
```

#### Example 4: Time Series Trend Analysis
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_cross_table

# Maternal mortality reduction
table = get_cross_table(
    indicator_code="MDG_0000000001",
    countries="USA,GBR",
    years="2000:2020"
)

print("Maternal Mortality Reduction (2000-2020)")
print("-" * 60)

for row in table.get('rows', []):
    country = row.get('country')
    values = []

    for year in range(2000, 2021):
        value = row.get(str(year))
        if value:
            values.append(value)

    if len(values) >= 2:
        reduction = ((values[0] - values[-1]) / values[0]) * 100
        print(f"{country}: {values[0]:.1f} → {values[-1]:.1f} per 100,000")
        print(f"       {reduction:.1f}% reduction")

# Output:
# Maternal Mortality Reduction (2000-2020)
# ------------------------------------------------------------
# USA: 17.0 → 23.8 per 100,000
#        -40.0% increase (worsening)
# GBR: 7.8 → 10.0 per 100,000
#        -28.2% increase (worsening)
```

---

## Common Use Cases

### Use Case 1: Life Expectancy Trend Analysis
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

def analyze_life_expectancy_trend(country_code, start_year, end_year):
    """Analyze life expectancy trend for a country"""

    # Get time series data
    data = get_country_data(
        indicator_code="WHOSIS_000001",
        country_code=country_code,
        year=f"{start_year}:{end_year}"
    )

    # Extract time series
    time_series = []
    for record in data.get('value', []):
        year = record.get('TimeDim')
        value = record.get('NumericValue')
        if year and value:
            time_series.append((year, value))

    time_series.sort()

    if len(time_series) >= 2:
        # Calculate metrics
        start_val = time_series[0][1]
        end_val = time_series[-1][1]
        change = end_val - start_val
        years_span = time_series[-1][0] - time_series[0][0]
        annual_change = change / years_span

        print(f"\nLife Expectancy Analysis: {country_code} ({start_year}-{end_year})")
        print("=" * 60)
        print(f"Starting value ({time_series[0][0]}): {start_val:.2f} years")
        print(f"Ending value ({time_series[-1][0]}): {end_val:.2f} years")
        print(f"Total change: {change:+.2f} years")
        print(f"Annual change: {annual_change:+.3f} years/year")
        print(f"Percent change: {(change/start_val)*100:+.2f}%")

        # Year-by-year
        print(f"\nYear-by-Year Trend:")
        for year, value in time_series:
            print(f"  {year}: {value:.2f} years")

    return time_series

# Analyze USA
analyze_life_expectancy_trend("USA", 2010, 2020)

# Analyze Japan for comparison
analyze_life_expectancy_trend("JPN", 2010, 2020)
```

### Use Case 2: Health Expenditure Comparison
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_cross_table

def compare_health_expenditure(countries, year):
    """Compare health expenditure across countries"""

    # Get cross-table data
    table = get_cross_table(
        indicator_code="GHED_CHE_pc_PPP_INT",
        countries=countries,
        years=str(year)
    )

    # Extract and rank
    country_data = []
    for row in table.get('rows', []):
        country = row.get('country')
        value = row.get(str(year))
        if value:
            country_data.append((country, value))

    country_data.sort(key=lambda x: x[1], reverse=True)

    print(f"\nHealth Expenditure per Capita Comparison ({year})")
    print("=" * 60)
    print(f"Countries: {countries}")
    print("-" * 60)

    for rank, (country, value) in enumerate(country_data, 1):
        print(f"{rank:2d}. {country:5s} ${value:8,.0f}")

    # Calculate statistics
    values = [v for _, v in country_data]
    avg = sum(values) / len(values)
    print(f"\nAverage: ${avg:,.0f}")
    print(f"Range: ${min(values):,.0f} - ${max(values):,.0f}")

    return country_data

# Compare OECD countries
oecd = "USA,GBR,JPN,DEU,FRA,ITA,CAN,AUS,KOR,ESP"
compare_health_expenditure(oecd, 2019)
```

### Use Case 3: Regional Disease Burden Assessment
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import (
    search_indicators,
    get_country_data,
    get_dimension_codes
)

def assess_regional_disease_burden(region_code, disease_keyword, year):
    """Assess disease burden across a WHO region"""

    # Step 1: Find disease indicator
    indicators = search_indicators(keywords=disease_keyword)

    if not indicators.get('indicators'):
        print(f"No indicators found for: {disease_keyword}")
        return

    indicator_code = indicators['indicators'][0]['code']
    indicator_name = indicators['indicators'][0]['name']

    print(f"\nRegional Disease Burden Assessment")
    print("=" * 80)
    print(f"Region: {region_code}")
    print(f"Indicator: {indicator_name}")
    print(f"Code: {indicator_code}")
    print(f"Year: {year}")
    print("-" * 80)

    # Step 2: Get regional data
    data = get_country_data(
        indicator_code=indicator_code,
        region_code=region_code,
        year=str(year),
        top=100
    )

    # Step 3: Analyze distribution
    country_values = []
    for record in data.get('value', []):
        country = record.get('SpatialDim')
        value = record.get('NumericValue')
        if value:
            country_values.append((country, value))

    country_values.sort(key=lambda x: x[1], reverse=True)

    # Statistics
    values = [v for _, v in country_values]
    if values:
        print(f"\nRegional Statistics:")
        print(f"  Countries: {len(values)}")
        print(f"  Average: {sum(values)/len(values):.2f}")
        print(f"  Median: {sorted(values)[len(values)//2]:.2f}")
        print(f"  Range: {min(values):.2f} - {max(values):.2f}")

        print(f"\nHighest Burden (Top 5):")
        for rank, (country, value) in enumerate(country_values[:5], 1):
            print(f"  {rank}. {country}: {value:.2f}")

        print(f"\nLowest Burden (Bottom 5):")
        for rank, (country, value) in enumerate(country_values[-5:], 1):
            print(f"  {rank}. {country}: {value:.2f}")

    return country_values

# Assess tuberculosis in African region
assess_regional_disease_burden("AFR", "tuberculosis incidence", 2020)
```

### Use Case 4: Gender Gap Analysis
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

def analyze_gender_gap(indicator_code, indicator_name, countries, year):
    """Analyze gender gap for a health indicator across countries"""

    print(f"\nGender Gap Analysis: {indicator_name} ({year})")
    print("=" * 80)

    country_list = countries.split(',')
    gaps = []

    for country in country_list:
        # Get male data
        male_data = get_country_data(
            indicator_code=indicator_code,
            country_code=country,
            year=str(year),
            sex="MLE"
        )

        # Get female data
        female_data = get_country_data(
            indicator_code=indicator_code,
            country_code=country,
            year=str(year),
            sex="FMLE"
        )

        male_val = male_data.get('value', [{}])[0].get('NumericValue')
        female_val = female_data.get('value', [{}])[0].get('NumericValue')

        if male_val and female_val:
            gap = female_val - male_val
            gap_pct = (gap / male_val) * 100
            gaps.append((country, male_val, female_val, gap, gap_pct))

    # Sort by gap size
    gaps.sort(key=lambda x: abs(x[3]), reverse=True)

    print(f"\n{'Country':<10} {'Male':>10} {'Female':>10} {'Gap':>10} {'Gap %':>10}")
    print("-" * 60)

    for country, male_val, female_val, gap, gap_pct in gaps:
        print(f"{country:<10} {male_val:10.2f} {female_val:10.2f} "
              f"{gap:+10.2f} {gap_pct:+9.1f}%")

    # Summary statistics
    avg_gap = sum(g[3] for g in gaps) / len(gaps)
    print(f"\nAverage gender gap: {avg_gap:+.2f} ({(avg_gap/sum(g[1] for g in gaps)*len(gaps))*100:+.1f}%)")

    return gaps

# Analyze life expectancy gender gap
countries = "USA,GBR,JPN,DEU,FRA,ITA,CAN,AUS"
analyze_gender_gap(
    indicator_code="WHOSIS_000001",
    indicator_name="Life Expectancy at Birth",
    countries=countries,
    year=2020
)
```

### Use Case 5: Multi-Indicator Country Profile
```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import get_country_data

def create_country_health_profile(country_code, year):
    """Create comprehensive health profile for a country"""

    # Define key indicators
    indicators = {
        'WHOSIS_000001': 'Life Expectancy at Birth',
        'MDG_0000000001': 'Maternal Mortality Ratio',
        'WHS9_86': 'Infant Mortality Rate',
        'GHED_CHE_pc_PPP_INT': 'Health Expenditure per Capita',
        'M_Est_smk_curr_std': 'Smoking Prevalence'
    }

    print(f"\nCountry Health Profile: {country_code} ({year})")
    print("=" * 80)

    for code, name in indicators.items():
        data = get_country_data(
            indicator_code=code,
            country_code=country_code,
            year=str(year)
        )

        if data.get('value'):
            value = data['value'][0].get('NumericValue')
            if value:
                print(f"\n{name}:")
                print(f"  Value: {value:.2f}")

                # Get 5-year historical for trend
                hist_data = get_country_data(
                    indicator_code=code,
                    country_code=country_code,
                    year=f"{year-5}:{year}"
                )

                values = []
                for record in hist_data.get('value', []):
                    val = record.get('NumericValue')
                    if val:
                        values.append(val)

                if len(values) >= 2:
                    trend = values[-1] - values[0]
                    print(f"  5-year trend: {trend:+.2f}")

# Create profile for USA
create_country_health_profile("USA", 2020)
```

---

## Best Practices

### ✅ DO

1. **Use Two-Step Workflow**
   ```python
   # Search for indicators first
   results = search_indicators(keywords="maternal mortality")
   code = results['indicators'][0]['code']

   # Then query with exact code
   data = get_health_data(indicator_code=code)
   ```

2. **Filter Data Server-Side**
   ```python
   # ✅ Good - filter at query time
   data = get_health_data(
       indicator_code="WHOSIS_000001",
       filter="SpatialDim eq 'USA' and TimeDim eq 2020"
   )

   # Instead of fetching all and filtering client-side
   ```

3. **Use Appropriate Method for Task**
   ```python
   # Simple country query → use get_country_data
   data = get_country_data(indicator_code="WHOSIS_000001", country_code="USA")

   # Complex filtering → use get_health_data with filter
   data = get_health_data(
       indicator_code="WHOSIS_000001",
       filter="TimeDim ge 2010 and Dim1 ne null"
   )

   # Cross-country table → use get_cross_table
   table = get_cross_table(
       indicator_code="WHOSIS_000001",
       countries="USA,GBR,CHN"
   )
   ```

4. **Check for Disaggregation**
   ```python
   # Check if sex-disaggregated data available
   data = get_health_data(
       indicator_code="WHOSIS_000001",
       filter="SpatialDim eq 'USA' and Dim1 ne null"
   )

   if data.get('value'):
       print("Sex-disaggregated data available")
   ```

5. **Handle Missing Data**
   ```python
   for record in data.get('value', []):
       value = record.get('NumericValue')
       if value is not None:  # Check for None, not just falsy
           print(f"Value: {value}")
   ```

### ❌ DON'T

1. **Don't Guess Indicator Codes**
   ```python
   # ❌ Wrong - guessing codes
   data = get_health_data(indicator_code="life_expectancy")

   # ✅ Correct - search first
   results = search_indicators(keywords="life expectancy")
   code = results['indicators'][0]['code']
   ```

2. **Don't Use Non-Standard Filter Syntax**
   ```python
   # ❌ Wrong - SQL syntax
   filter="country='USA' AND year>=2015"

   # ✅ Correct - OData syntax
   filter="SpatialDim eq 'USA' and TimeDim ge 2015"
   ```

3. **Don't Fetch All Data Without Filters**
   ```python
   # ❌ Wrong - fetches entire database
   data = get_health_data(indicator_code="WHOSIS_000001")

   # ✅ Correct - filter at query time
   data = get_health_data(
       indicator_code="WHOSIS_000001",
       filter="TimeDim eq 2020"
   )
   ```

4. **Don't Use Generic Terms for Dimensions**
   ```python
   # ❌ Wrong - generic terms
   filter="country eq 'USA'"
   filter="sex eq 'male'"

   # ✅ Correct - WHO dimension codes
   filter="SpatialDim eq 'USA'"
   filter="Dim1 eq 'MLE'"
   ```

5. **Don't Assume All Indicators Have Sex Disaggregation**
   ```python
   # ❌ Wrong - assume disaggregation exists
   data = get_health_data(
       indicator_code=some_code,
       filter="Dim1 eq 'MLE'"
   )
   # May return no results if indicator not disaggregated

   # ✅ Correct - check first
   check = get_health_data(
       indicator_code=some_code,
       filter="Dim1 ne null",
       top=1
   )
   if check.get('value'):
       # Disaggregation available, query specific sex
       data = get_health_data(
           indicator_code=some_code,
           filter="Dim1 eq 'MLE'"
       )
   ```

---

## Frequently Asked Questions

### Q1: How do I find the right indicator code?

Use `search_indicators` with keywords:
```python
results = search_indicators(keywords="maternal mortality")

for indicator in results.get('indicators', []):
    code = indicator.get('code')
    name = indicator.get('name')
    print(f"{code}: {name}")

# Pick the appropriate code for your analysis
```

### Q2: What's the difference between SpatialDim and country codes?

`SpatialDim` is the field name in OData queries, country codes are the values:
```python
# SpatialDim is the field, USA is the country code
filter="SpatialDim eq 'USA'"

# Get all country codes
countries = get_dimension_codes(dimension_code="COUNTRY")
```

### Q3: How do I query for a specific year range?

Use OData `ge` (greater or equal) and `le` (less or equal):
```python
# 2015-2020 range
filter="TimeDim ge 2015 and TimeDim le 2020"

# Or use get_country_data with year range
data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2015:2020"
)
```

### Q4: How do I get sex-disaggregated data?

Check for disaggregation, then query specific sex:
```python
# Check if disaggregated
check = get_health_data(
    indicator_code="WHOSIS_000001",
    filter="SpatialDim eq 'USA' and Dim1 ne null",
    top=1
)

if check.get('value'):
    # Get male data
    male = get_health_data(
        indicator_code="WHOSIS_000001",
        filter="SpatialDim eq 'USA' and Dim1 eq 'MLE'"
    )

    # Get female data
    female = get_health_data(
        indicator_code="WHOSIS_000001",
        filter="SpatialDim eq 'USA' and Dim1 eq 'FMLE'"
    )
```

### Q5: What WHO regions are available?

Six WHO regions:
```python
regions = get_dimension_codes(dimension_code="REGION")

# AFR - African Region
# AMR - Region of the Americas
# SEAR - South-East Asia Region
# EUR - European Region
# EMR - Eastern Mediterranean Region
# WPR - Western Pacific Region
```

### Q6: How do I compare multiple countries?

Use `get_cross_table` for clean tabular output:
```python
table = get_cross_table(
    indicator_code="WHOSIS_000001",
    countries="USA,GBR,JPN,DEU,FRA",
    years="2015:2020"
)

# Returns structured table with countries as rows, years as columns
```

### Q7: Can I get all data for a region at once?

Yes, use `get_country_data` with `region_code`:
```python
# All European countries
data = get_country_data(
    indicator_code="WHOSIS_000001",
    region_code="EUR",
    year="2020",
    top=100
)

# Returns data for all countries in European region
```

### Q8: How do I handle missing data?

Check for `None` values explicitly:
```python
for record in data.get('value', []):
    value = record.get('NumericValue')
    low = record.get('Low')
    high = record.get('High')

    if value is not None:  # Explicit check
        print(f"Value: {value}")

        if low and high:
            print(f"Range: {low} - {high}")
```

### Q9: What's the difference between get_health_data and get_country_data?

- `get_health_data`: Advanced OData filtering, full control
- `get_country_data`: Simplified interface, common queries

Use `get_country_data` for simple queries, `get_health_data` for complex filtering:
```python
# Simple query - use get_country_data
data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2020"
)

# Complex query - use get_health_data
data = get_health_data(
    indicator_code="WHOSIS_000001",
    filter="TimeDim ge 2010 and (SpatialDim eq 'USA' or SpatialDim eq 'CAN') and Dim1 ne null"
)
```

### Q10: How do I calculate growth rates or trends?

Query time series, then calculate:
```python
data = get_country_data(
    indicator_code="WHOSIS_000001",
    country_code="USA",
    year="2010:2020"
)

# Extract values
time_series = []
for record in data.get('value', []):
    year = record.get('TimeDim')
    value = record.get('NumericValue')
    if year and value:
        time_series.append((year, value))

time_series.sort()

# Calculate annual growth rate
if len(time_series) >= 2:
    start_val = time_series[0][1]
    end_val = time_series[-1][1]
    years = time_series[-1][0] - time_series[0][0]

    annual_change = (end_val - start_val) / years
    cagr = (((end_val / start_val) ** (1 / years)) - 1) * 100

    print(f"Annual change: {annual_change:+.3f}")
    print(f"CAGR: {cagr:+.2f}%")
```

---

## Token Usage Guidelines

| Query Type | Approx. Tokens | Recommendation |
|------------|---------------|----------------|
| Search indicators | 300-800 | ✅ Efficient for discovery |
| Single country-year | 50-100 | ✅ Excellent for specific queries |
| 10-year time series | 100-500 | ✅ Good for trend analysis |
| Regional query (50 countries) | 500-2,000 | ⚠️ Use top parameter to limit |
| Cross-table (5 countries, 10 years) | 100-500 | ✅ Efficient for comparisons |
| Full indicator (no filter) | 5,000-50,000 | 🔴 Always use filters |

**Token Optimization Tips**:
1. Always filter by country and/or time range
2. Use `top` parameter to limit large datasets
3. Request only needed sex disaggregation
4. Use `get_country_data` for simple queries (auto-optimized)
5. Use `get_cross_table` for multi-country comparisons (structured output)

---

## Integration with Other MCP Servers

### WHO + ClinicalTrials.gov (Disease Burden → Trials)
```python
# Step 1: Get disease burden from WHO
from mcp.servers.who_mcp import search_indicators, get_country_data

results = search_indicators(keywords="diabetes prevalence")
diabetes_code = results['indicators'][0]['code']

diabetes_data = get_country_data(
    indicator_code=diabetes_code,
    country_code="USA",
    year="2020"
)

burden = diabetes_data['value'][0]['NumericValue']
print(f"US Diabetes Prevalence: {burden}%")

# Step 2: Find diabetes trials
from mcp.servers.ct_gov_mcp import search

trials = search(
    condition="diabetes",
    status="recruiting",
    location="United States",
    pageSize=50
)

print(f"\nActive diabetes trials: {trials.count('NCT')}")
```

### WHO + FDA (Health Outcomes → Approved Drugs)
```python
# Step 1: Assess health outcome
from mcp.servers.who_mcp import get_country_data

obesity_data = get_country_data(
    indicator_code="NCD_BMI_30A",  # Obesity prevalence
    country_code="USA",
    year="2020"
)

# Step 2: Find approved obesity drugs
from mcp.servers.fda_mcp import lookup_drug

fda_results = lookup_drug(
    search_term="obesity",
    search_type="general",
    count="openfda.brand_name.exact",
    limit=25
)

print(f"Approved obesity treatments: {len(fda_results.get('results', []))}")
```

---

## Summary

**WHO MCP Server** provides comprehensive access to global health statistics via OData protocol:

✅ **6 flexible methods** for different query patterns
✅ **Standard OData syntax** for powerful filtering
✅ **Sex disaggregation** available for many indicators
✅ **Time series analysis** with year range filtering
✅ **Regional queries** across WHO's 6 regions
✅ **Cross-country comparisons** with tabular output

**Key Pattern**: Search indicators → Get indicator code → Query data with filters

**Token Efficient**: 50-500 tokens for typical queries (with proper filtering)

**Perfect For**: Population health analysis, disease burden assessment, health system comparisons, epidemiological research, global health monitoring
