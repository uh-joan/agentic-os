---
name: forecast_drug_pipeline
description: >
  Generic drug pipeline forecasting tool with flexible search criteria. Searches ClinicalTrials.gov
  for trials matching specified criteria (route, therapeutic area, sponsor, intervention type),
  filters by completion years, and forecasts approval timeline based on configurable FDA review offset.
  Supports multiple use cases: route-based forecasting (subcutaneous, oral, intravenous),
  therapeutic area analysis, sponsor-specific pipeline, and multi-criteria searches.

  Trigger keywords: pipeline forecast, drug approval forecast, administration route, oral drugs,
  subcutaneous, intravenous, inhalation, pipeline analysis, approval timeline, completion forecast.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - cli_arguments
  - pagination
  - markdown_parsing
  - temporal_filtering
  - therapeutic_area_analysis
  - parameterized_search
data_scope:
  total_results: Variable (depends on search criteria)
  filtered_results: Variable (depends on completion years)
  geographical: Global
  temporal: Configurable (default: current year + future years)
created: 2025-11-25
last_updated: 2025-11-25
complexity: medium
execution_time: ~5-15 minutes (depends on result set size)
token_efficiency: ~99% reduction vs raw data
cli_enabled: true
---
# forecast_drug_pipeline



## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for forecast drug pipeline?`
2. `@agent-pharma-search-specialist Find active forecast drug pipeline trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for forecast drug pipeline`


## CLI Usage

```bash
# Subcutaneous drugs for 2026-2027 approval
python forecast_drug_pipeline.py --route subcutaneous --completion-years 2024 2025

# Oral diabetes drugs
python forecast_drug_pipeline.py --route oral --therapeutic-area diabetes --completion-years 2025 2026

# Company-specific pipeline
python forecast_drug_pipeline.py --sponsor "Pfizer" --intervention-type biological --completion-years 2024 2025
```

## Parameters

- **--route** (str, optional): Administration route (subcutaneous, oral, intravenous, inhalation)
- **--therapeutic-area** (str, optional): Disease/condition (diabetes, cancer, Alzheimer)
- **--sponsor** (str, optional): Company name (Pfizer, Moderna, Eli Lilly)
- **--intervention-type** (str, optional): Type (drug, biological, device)
- **--completion-years** (int list, optional): Trial completion years (default: 2024 2025)
- **--phase** (str, optional): Clinical trial phase (default: PHASE3)
- **--approval-offset** (int, optional): Years after completion to forecast approval (default: 2)

## Returns

Pipeline forecast with approval timeline projections and therapeutic area breakdown.
## Purpose

A flexible, parameterized drug pipeline forecasting tool that predicts approval timelines based on clinical trial completion dates. Unlike single-purpose skills, this tool accepts configurable search criteria to support diverse use cases:

- **Route-based forecasting**: Subcutaneous, oral, intravenous, inhalation drugs
- **Therapeutic area analysis**: Diabetes, oncology, cardiovascular, CNS pipelines
- **Sponsor-specific pipeline**: Company-specific approval forecasts
- **Multi-criteria searches**: Combine route + therapeutic area + sponsor

## Key Innovation

**Parameterized Design**: Single skill replaces dozens of specific skills by accepting flexible search criteria as a dictionary.

## Function Signature

```python
def forecast_drug_pipeline(
    search_criteria,
    completion_years=None,
    phase="PHASE3",
    approval_offset_years=2
):
    """Forecast drug pipeline with flexible search criteria.

    Args:
        search_criteria: Dict with keys like:
            - route: Administration route (e.g., "subcutaneous", "oral", "intravenous", "inhalation")
            - therapeutic_area: Disease/condition (e.g., "diabetes", "cancer", "Alzheimer")
            - sponsor: Company name (e.g., "Pfizer", "Moderna", "Eli Lilly")
            - intervention_type: Drug, biological, device
        completion_years: List of years for trial completion (default: [2024, 2025])
        phase: Clinical trial phase (default: "PHASE3")
        approval_offset_years: Years after completion to forecast approval (default: 2)

    Returns:
        dict: Contains total_count, target_count, trials, summary, and forecast

    Examples:
        # Subcutaneous drugs for 2026-2027 approval
        forecast_drug_pipeline({"route": "subcutaneous"}, [2024, 2025])

        # Oral diabetes drugs for 2027-2028 approval
        forecast_drug_pipeline(
            {"route": "oral", "therapeutic_area": "diabetes"},
            [2025, 2026]
        )

        # Pfizer biologics for 2026-2027 approval
        forecast_drug_pipeline(
            {"sponsor": "Pfizer", "intervention_type": "biological"},
            [2024, 2025]
        )
    """
```

## Usage Examples

### Example 1: Route-Based Forecasting

**Subcutaneous drugs (2026-2027 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"route": "subcutaneous"},
    completion_years=[2024, 2025]
)
```

**Oral drugs (2027-2028 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"route": "oral"},
    completion_years=[2025, 2026]
)
```

**Intravenous drugs (2026-2027 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"route": "intravenous"},
    completion_years=[2024, 2025]
)
```

### Example 2: Therapeutic Area Analysis

**Diabetes pipeline (2026-2027 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"therapeutic_area": "diabetes"},
    completion_years=[2024, 2025]
)
```

**Alzheimer's pipeline (2027-2028 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"therapeutic_area": "Alzheimer"},
    completion_years=[2025, 2026]
)
```

### Example 3: Sponsor-Specific Pipeline

**Pfizer pipeline (2026-2027 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"sponsor": "Pfizer"},
    completion_years=[2024, 2025]
)
```

**Moderna biologics (2027-2028 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={"sponsor": "Moderna", "intervention_type": "biological"},
    completion_years=[2025, 2026]
)
```

### Example 4: Multi-Criteria Search

**Oral diabetes drugs (2026-2027 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={
        "route": "oral",
        "therapeutic_area": "diabetes"
    },
    completion_years=[2024, 2025]
)
```

**Pfizer subcutaneous biologics (2027-2028 approval)**
```python
result = forecast_drug_pipeline(
    search_criteria={
        "route": "subcutaneous",
        "sponsor": "Pfizer",
        "intervention_type": "biological"
    },
    completion_years=[2025, 2026]
)
```

### Example 5: Custom Approval Timeline

**Phase 2 trials (3-year approval offset)**
```python
result = forecast_drug_pipeline(
    search_criteria={"route": "subcutaneous"},
    completion_years=[2024, 2025],
    phase="PHASE2",
    approval_offset_years=3  # Phase 2 typically takes longer
)
```

## Data Collected

The skill retrieves and analyzes:

- **All trials matching search criteria** (complete dataset, no sampling)
- **Trial details**: NCT ID, title, condition, intervention, status, completion date
- **Therapeutic area distribution**: Top disease areas
- **Sponsor analysis**: Leading companies
- **Completion timeline**: Breakdown by year
- **Status distribution**: Recruiting, active, completed trial counts

## Implementation Details

### Search Query Builder

Combines multiple search criteria into CT.gov query:

```python
def build_search_term(search_criteria):
    """Build CT.gov search term from criteria dict."""
    terms = []

    if 'route' in search_criteria:
        terms.append(search_criteria['route'])

    if 'therapeutic_area' in search_criteria:
        terms.append(search_criteria['therapeutic_area'])

    if 'intervention_type' in search_criteria:
        terms.append(search_criteria['intervention_type'])

    # Sponsor handled separately (CT.gov has sponsor parameter)
    return ' '.join(terms) if terms else None
```

### Optimal Pagination Strategy

Uses efficient pagination to retrieve ALL trials (orphan drugs pattern):

```python
# Step 1: Quick query with pageSize=1 to get total count
result_preview = search(**search_params)
total_available = extract_total(result_preview)

# Step 2: Calculate optimal pageSize to fetch all in 2 pages
optimal_page_size = ceil(total_available / 2)

# Step 3: Fetch all trials with optimal page size
while True:
    result = search(**search_params)
    # Extract NCT IDs...
    if next_token:
        continue
    else:
        break  # All trials collected
```

### Markdown Parsing

Extracts structured data from CT.gov markdown using regex:

```python
# Split by NCT ID headers
trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

# Extract fields from each trial block
title_match = re.search(r'\*\*Brief Title:\*\*\s*(.+?)(?:\n|$)', block)
completion_match = re.search(r'\*\*Study Completion:\*\*\s*(.+?)(?:\n|$)', block)
```

### Temporal Filtering

Applies approval timeline logic with configurable offset:

```python
# Calculate forecast approval years
forecast_years = [year + approval_offset_years for year in completion_years]

# Filter trials by completion year
year_match = re.search(r'(2024|2025|2026|2027)', completion_date)
if year_match:
    year = int(year_match.group(1))
    if year in completion_years:
        target_trials.append(trial)
```

## Output Format

Returns a dictionary with:

```python
{
    'total_count': 2002,           # All trials matching criteria
    'target_count': 189,           # Likely approval in forecast window
    'trials': [...],               # List of trial dictionaries
    'summary': {
        'total_trials': 2002,
        'likely_approval': 189,
        'top_therapeutic_areas': [...],
        'top_sponsors': [...],
        'status_distribution': {...},
        'completion_years_breakdown': {
            '2024': 89,
            '2025': 100
        }
    },
    'forecast': {
        'years': '2026-2027',
        'completion_years': [2024, 2025],
        'approval_offset': 2,
        'search_criteria': {"route": "subcutaneous"}
    }
}
```

## Approval Timeline Logic

The skill applies a probabilistic forecasting model:

1. **Search scope**: Configurable phase (default: Phase 3 - final efficacy stage)
2. **Search criteria**: Flexible (route, therapeutic area, sponsor, intervention type)
3. **Completion window**: Configurable years (default: 2024-2025)
4. **FDA review timeline**: Configurable offset (default: 2 years)
5. **Approval forecast**: Completion years + offset = approval years

**Example**:
- Completion years: [2024, 2025]
- Approval offset: 2 years
- Forecast: 2026-2027 approval

**Rationale**: Phase 3 trials completing in 2024-2025 will submit for approval upon completion. Standard FDA review takes 10-24 months (default offset: 2 years), placing approval in the 2026-2027 timeframe.

## Key Insights

**Flexibility**: Single skill supports unlimited use cases via parameterized search

**Completeness**: No sampling - retrieves complete dataset for accurate forecasts

**Configurability**: Adjustable completion years and approval offset for different scenarios

**Consistency**: Uses proven patterns from validated skills (orphan drugs, subcutaneous drugs)

## Limitations

- **Probabilistic forecast**: Not all Phase 3 trials succeed; some may fail or delay
- **FDA variability**: Review times vary; Priority Review can accelerate, safety issues can delay
- **Completion date accuracy**: Trial timelines often shift; dates are estimates
- **Search term matching**: Relies on keyword matching in trial data; may miss variations

## Strategic Applications

**For Pharmaceutical Companies**:
- Forecast competitive pipeline by route, therapeutic area, or competitor
- Plan commercial launch strategies for specific approval windows
- Identify white space opportunities (underserved routes/areas)

**For Investors**:
- Evaluate biotech companies with near-term approval catalysts
- Assess market timing for specific drug delivery platforms or therapeutic areas
- Identify partnership/acquisition targets by sponsor-specific forecasting

**For Strategic Planners**:
- Forecast market dynamics for specific approval windows
- Analyze route trends (shift to patient-friendly administration)
- Plan R&D priorities based on competitive landscape

**For Healthcare Providers**:
- Anticipate new treatment options by therapeutic area
- Plan for patient education on new administration routes
- Evaluate cost implications of upcoming approvals

## Related Skills

- `get_subcutaneous_drugs_pipeline_2026_2027` - Validated reference implementation for subcutaneous drugs
- `get_orphan_drugs_upcoming_approvals` - Orphan drug pipeline with approval likelihood scoring
- `get_{therapeutic_area}_trials` - Therapeutic area-specific trial searches
- `get_{company}_pipeline` - Company-specific pipeline analysis

## Example Output

```
================================================================================
DRUG PIPELINE FORECAST: 2026-2027 APPROVAL
================================================================================

Search Criteria: {'route': 'subcutaneous'}
Total subcutaneous trials: 2002
Trials likely for 2026-2027 approval: 189

Completion Timeline:
  • Completing in 2024: 89 trials
  • Completing in 2025: 100 trials

Trial Status Distribution:
  • Completed: 108 trials
  • Active Not Recruiting: 25 trials
  • Recruiting: 18 trials

Top Therapeutic Areas:
  1. Atopic Dermatitis: 9 trials
  2. Multiple Myeloma: 7 trials
  3. Asthma: 6 trials
  4. Generalized Myasthenia Gravis: 3 trials
  5. Type 2 Diabetes: 3 trials

Top Sponsors:
  1. Janssen Research & Development: 10 trials
  2. Eli Lilly and Company: 7 trials
  3. Sanofi: 6 trials
  4. Novartis Pharmaceuticals: 6 trials
  5. Amgen: 6 trials

================================================================================
FORECAST METHODOLOGY
================================================================================

Approval Timeline Rationale:
• Phase 3 trials completing in [2024, 2025]
• Typical FDA review: 2 years
• Expected approval window: 2026-2027

Note: This is a probabilistic forecast based on completion dates.
Actual approval depends on trial results, FDA review speed, and regulatory factors.
```