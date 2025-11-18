# get_phase2_alzheimers_trials_us

## Purpose
Find Phase 2 clinical trials for Alzheimer's disease that are actively recruiting in the United States.

## Usage
```python
from .claude.skills.get_phase2_alzheimers_trials_us import get_phase2_alzheimers_trials_us

results = get_phase2_alzheimers_trials_us()
print(f"Found {results['total_trials']} trials")
```

## Returns
Dictionary with:
- `total_trials`: Number of trials found
- `unique_sponsors`: Number of unique sponsors
- `total_enrollment`: Total planned enrollment
- `trials`: List of trial dictionaries (nct_id, title, sponsor, enrollment, etc.)
- `sponsor_list`: Sorted list of unique sponsors

## MCP Server
- **Server**: ct_gov_mcp
- **Tool**: ct_gov_studies
- **Parameters**: query="Alzheimer's disease", phase="PHASE2", status="RECRUITING", location="United States"

## Example Output
```
Total Trials Found: 75
Unique Sponsors: 67
Total Planned Enrollment: 16,772 participants
```

## Created
2025-11-18
