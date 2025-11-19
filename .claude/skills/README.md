# Skills Library

Reusable data collection functions for pharmaceutical research intelligence.

## Overview

This directory contains validated, executable skills that collect and process data from MCP servers. Each skill follows the two-phase persistence pattern and includes:

- ✅ **Importable function** for programmatic use
- ✅ **Executable script** with `if __name__ == "__main__"` block
- ✅ **Data validation** to ensure quality
- ✅ **Documentation** (.md file with usage examples)

Following Anthropic's "Code execution with MCP" pattern:
https://www.anthropic.com/engineering/code-execution-with-mcp

## Pattern

When pharma-search-specialist generates code to answer a query, it:

1. **Defines a reusable function** that encapsulates the query logic
2. **Executes the function** and displays results to the user
3. **Saves the function** to this directory for future reuse

## Structure

```
.claude/skills/
├── index.json                      # Machine-readable skills metadata
├── README.md                       # Human-readable documentation (this file)
├── get_kras_inhibitor_trials.py    # KRAS inhibitor trials collection
├── get_kras_inhibitor_trials.md    # Documentation
├── get_kras_inhibitor_fda_drugs.py # KRAS FDA approved drugs
└── get_kras_inhibitor_fda_drugs.md # Documentation
```

## Discovery

**For agents**: Read `index.json` to discover available skills programmatically
**For humans**: Read this README or individual `.md` files

## Available Skills

### Clinical Trials

#### `get_kras_inhibitor_trials`
- **Purpose**: Get KRAS inhibitor clinical trials across all phases
- **Returns**: `{total_count: int, trials_summary: str}`
- **Execute**: `PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/kras-inhibitor-trials/scripts/get_kras_inhibitor_trials.py`

### FDA Drugs

#### `get_kras_inhibitor_fda_drugs`
- **Purpose**: Get FDA approved KRAS inhibitor drugs
- **Returns**: `{brand_name: {generic: str, count: int}}`
- **Execute**: `PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/kras-inhibitor-fda-drugs/scripts/get_kras_inhibitor_fda_drugs.py`

## Usage

### Import and Use

```python
from .claude.skills.kras_inhibitor_trials.scripts.get_kras_inhibitor_trials import get_kras_inhibitor_trials
from .claude.skills.kras_inhibitor_fda_drugs.scripts.get_kras_inhibitor_fda_drugs import get_kras_inhibitor_fda_drugs

# Use the functions
trials = get_kras_inhibitor_trials()
drugs = get_kras_inhibitor_fda_drugs()

print(f"Found {trials['total_count']} trials")
print(f"Found {len(drugs)} approved drugs")
```

### Execute Standalone

```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/kras-inhibitor-trials/scripts/get_kras_inhibitor_trials.py
```

## Benefits (per Anthropic)

1. **Build Toolbox**: Accumulate higher-level capabilities over time
2. **Evolving Expertise**: Agent builds persistent knowledge across sessions
3. **Reusability**: Don't rewrite common query patterns
4. **Composability**: Combine functions to answer complex queries

## Skill Standards

**Every skill must be both importable AND executable**:

```python
import sys
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_kras_inhibitor_trials():
    """Get KRAS inhibitor clinical trials across all phases.

    Returns:
        dict: Contains total_count and trials_summary

    Raises:
        ValueError: If no trials found or validation fails
    """
    result = search(term="KRAS inhibitor", pageSize=100)

    # Validate response
    if not result:
        raise ValueError("No data returned from CT.gov API")

    # Extract count
    count_match = re.search(r'(\d+) studies found', result)
    if not count_match:
        raise ValueError("Could not parse trial count")

    total_count = int(count_match.group(1))
    if total_count == 0:
        raise ValueError("No trials found")

    return {'total_count': total_count, 'trials_summary': result}

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    try:
        result = get_kras_inhibitor_trials()
        print(f"✓ Data collection successful: {result['total_count']} trials")
        print(result['trials_summary'])
    except ValueError as e:
        print(f"✗ Data validation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
```

## Skill Patterns

Skills follow naming patterns based on data type and therapeutic area:

| Pattern | Example | Purpose |
|---------|---------|---------|
| `get_{therapeutic_area}_trials` | `get_kras_inhibitor_trials` | Clinical trials collection |
| `get_{therapeutic_area}_fda_drugs` | `get_kras_inhibitor_fda_drugs` | FDA approved drugs |
| `get_{therapeutic_area}_pubmed` | TBD | PubMed literature search |
| `get_{company}_trials` | TBD | Company-specific trials |

## Creating New Skills

See `.claude/.context/code-examples/skills_library_pattern.md` for detailed guidance.

**Quick checklist**:
1. ✅ Define reusable function with docstring
2. ✅ Add data validation (see `data_validation_pattern.md`)
3. ✅ Include `if __name__ == "__main__":` block
4. ✅ Test execution: `PYTHONPATH=scripts:$PYTHONPATH python3 skill.py`
5. ✅ Create documentation file (`.md`)
6. ✅ Update `index.json` with skill metadata

## Validation

All skills include validation to ensure data quality:

- ✅ Response type checking (dict vs string)
- ✅ Non-empty results (count > 0)
- ✅ Expected fields present
- ✅ Descriptive error messages

Failed validation raises `ValueError` with actionable error message.

## Progressive Disclosure

Skills are designed to minimize context usage:

- **Data processed in execution environment** (not in model context)
- **Only summaries flow to conversation** (98.7% token reduction)
- **Skills grow library over time** (evolutionary expertise)

## Maintenance

- ✅ Functions added automatically by agent-generated code
- ✅ Each function saved immediately after successful execution
- ✅ Skills are version controlled (`.claude/skills/` tracked in git)
- ✅ `index.json` updated when new skills added
