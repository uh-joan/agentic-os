# get_us_phase3_obesity_recruiting_trials

## Purpose
Get count of Phase 3 obesity clinical trials that are actively recruiting in the United States.

## Parameters
None

## Returns
- `int`: Number of Phase 3 obesity trials actively recruiting in the US

## Usage
```python
from .claude.skills.get_us_phase3_obesity_recruiting_trials import get_us_phase3_obesity_recruiting_trials
count = get_us_phase3_obesity_recruiting_trials()
print(f"Found {count} trials")
```

## Example Output
```
36
```

## MCP Tools Used
- ct_gov_studies (via ct-gov-mcp client)

## Query Parameters
- Condition: obesity
- Phase: PHASE3
- Status: recruiting
- Location: United States
