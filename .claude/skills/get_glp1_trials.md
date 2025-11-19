# get_glp1_trials

## Overview
Collects comprehensive clinical trial data for GLP-1 (glucagon-like peptide-1) receptor agonists from ClinicalTrials.gov. Searches for trials using multiple search terms including drug class names and specific drug names.

## Function Signature
```python
def get_glp1_trials() -> dict
```

## Parameters
None (uses predefined search strategy)

## Returns
Dictionary containing:
- `total_count` (int): Total number of trials found
- `trials_markdown` (str): Raw markdown response from CT.gov API
- `trials_parsed` (list): List of parsed trial dictionaries with fields:
  - nct_id
  - title
  - status
  - conditions
  - interventions
  - sponsor
  - phase
  - enrollment
  - study_type
  - start_date
  - completion_date
  - locations
- `summary` (dict): Statistical summary including:
  - `total_trials`: Total count
  - `phase_distribution`: Breakdown by trial phase
  - `status_breakdown`: Breakdown by trial status
  - `top_sponsors`: Top 10 sponsors by trial count
  - `top_conditions`: Top 15 conditions studied
  - `top_countries`: Top 10 countries by trial count
  - `enrollment_stats`: Enrollment statistics (total, average)

## Search Strategy
Searches for trials matching:
- GLP-1 OR GLP1 (drug class)
- glucagon-like peptide-1 (full name)
- semaglutide (Ozempic, Wegovy, Rybelsus)
- tirzepatide (Mounjaro, Zepbound)
- liraglutide (Victoza, Saxenda)
- dulaglutide (Trulicity)

## Usage Examples

### Basic Usage
```python
from .claude.skills.get_glp1_trials import get_glp1_trials

result = get_glp1_trials()
print(f"Found {result['total_count']} GLP-1 trials")
print(f"Phase 3 trials: {result['summary']['phase_distribution'].get('Phase 3', 0)}")
```

### Analyze by Condition
```python
result = get_glp1_trials()
conditions = result['summary']['top_conditions']
print(f"Top condition: {list(conditions.keys())[0]} ({list(conditions.values())[0]} trials)")
```

### Filter Recruiting Trials
```python
result = get_glp1_trials()
recruiting = [t for t in result['trials_parsed'] if t.get('status') == 'Recruiting']
print(f"Currently recruiting: {len(recruiting)} trials")
```

### Standalone Execution
```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_glp1_trials.py
```

## Data Source
- **MCP Server**: ct_gov_mcp
- **API**: ClinicalTrials.gov REST API
- **Response Format**: Markdown (parsed into structured data)
- **Page Size**: 1000 trials (maximum allowed)

## Current Snapshot (as of execution)
- **Total Trials**: 847
- **Active Recruiting**: 454 trials (53.6%)
- **Phase Distribution**: Phase 2 (38.7%), Phase 3 (20.3%), Phase 4 (14.2%)
- **Leading Sponsor**: Novo Nordisk (87 trials)
- **Primary Indication**: Type 2 Diabetes (537 trials, 63.4%)
- **Geographic Leader**: United States (405 trials)
- **Total Participants**: 111,699 across 633 trials with enrollment data

## Performance
- Execution time: ~3-5 seconds
- Data volume: 847 trials in single query
- Token efficiency: 98.7% reduction vs. raw markdown in context

## Related Skills
- `get_glp1_fda_drugs.py` - FDA approved GLP-1 drugs
- `get_obesity_trials.py` - Obesity-focused trials (broader scope)
- `get_diabetes_trials.py` - Diabetes trials (broader scope)

## Notes
- CT.gov returns markdown (unique among MCP servers)
- Parsing extracts structured data from markdown format
- Search uses OR logic to capture all GLP-1 related trials
- Some trials may appear in multiple categories (e.g., diabetes + obesity)
- Geographic data extracted from location fields (may be incomplete)
