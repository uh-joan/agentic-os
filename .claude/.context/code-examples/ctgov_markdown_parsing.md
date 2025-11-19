# ClinicalTrials.gov Markdown Parsing Pattern

## When to Use This Example
- Query involves ClinicalTrials.gov searches
- Need to parse trial counts, statuses, or basic trial info
- Server: `mcp.servers.ct_gov_mcp`

## Critical: Response Format
**CT.gov returns MARKDOWN STRING, not JSON!**

## Complete Working Example

```python
import sys
import re
sys.path.insert(0, 'scripts')
from pathlib import Path

from mcp.servers.ct_gov_mcp import search

# Reusable function
def get_us_phase3_obesity_recruiting_trials():
    """Get count of Phase 3 obesity trials recruiting in US."""
    result = search(
        condition="obesity",
        phase="PHASE3",
        status="recruiting",
        location="United States",
        pageSize=10
    )

    # CT.gov returns MARKDOWN string - parse with regex
    if isinstance(result, str):
        match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', result)
        if match:
            return int(match.group(1))
    return 0

# Execute and display
count = get_us_phase3_obesity_recruiting_trials()
print(f"Phase 3 obesity trials recruiting in US: {count}")

# Save to skills library
skill_path = Path('.claude/skills/get_us_phase3_obesity_recruiting_trials.py')
skill_path.parent.mkdir(parents=True, exist_ok=True)
skill_path.write_text('''import sys
import re
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_us_phase3_obesity_recruiting_trials():
    """Get count of Phase 3 obesity trials recruiting in US."""
    result = search(
        condition="obesity",
        phase="PHASE3",
        status="recruiting",
        location="United States",
        pageSize=10
    )

    if isinstance(result, str):
        match = re.search(r"\\\\*\\\\*Results:\\\\*\\\\* \\\\d+ of (\\\\d+) studies found", result)
        if match:
            return int(match.group(1))
    return 0
''')

# Save SKILL.md
skill_md = Path('.claude/skills/get_us_phase3_obesity_recruiting_trials.md')
skill_md.write_text('''# get_us_phase3_obesity_recruiting_trials

## Purpose
Get count of Phase 3 obesity trials recruiting in US.

## Returns
- `int`: Number of trials

## Usage
\`\`\`python
from .claude.skills.us_phase3_obesity_recruiting_trials.scripts.get_us_phase3_obesity_recruiting_trials import get_us_phase3_obesity_recruiting_trials
count = get_us_phase3_obesity_recruiting_trials()
\`\`\`

## MCP Tools Used
- ct_gov_mcp.search
''')
```

## Key Patterns

### 1. Always Import `re` Module
```python
import re
```

### 2. Check Response Type
```python
if isinstance(result, str):
    # Parse markdown
```

### 3. Extract Count with Regex
```python
match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', result)
if match:
    count = int(match.group(1))
```

### 4. Common Regex Patterns
```python
# Total count
r'\*\*Results:\*\* \d+ of (\d+) studies found'

# NCT ID
r'NCT\d{8}'

# Trial title
r'\*\*Title:\*\* (.+?)$'
```

## Parameter Reference
See `.claude/.context/mcp-tool-guides/clinicaltrials.md` for full parameter list.

Common parameters:
- `condition` - Medical condition (e.g., "obesity", "diabetes")
- `phase` - Trial phase: "PHASE1", "PHASE2", "PHASE3", "PHASE4"
- `status` - "recruiting", "completed", "active_not_recruiting"
- `location` - Geographic filter (e.g., "United States", "California")
- `pageSize` - Results per page (default: 10, max: 1000)
