# Skills Library

## Purpose

This directory contains **reusable functions** extracted by the `pharma-search-specialist` agent during code execution.

Following Anthropic's "Code execution with MCP" pattern:
https://www.anthropic.com/engineering/code-execution-with-mcp

## Pattern

When pharma-search-specialist generates code to answer a query, it:

1. **Defines a reusable function** that encapsulates the query logic
2. **Executes the function** and displays results to the user
3. **Saves the function** to this directory for future reuse

## Structure

Each file contains a single, well-documented function:

```
.claude/skills/
├── get_glp1_agonists.py          # Get all GLP-1 receptor agonists
├── search_drug_brands.py         # Search drug brands by term
├── search_nash_phase3_trials.py  # Search Phase 3 NASH trials
└── ...
```

## Usage

Future code executions can import these functions directly:

```python
from .claude.skills.get_glp1_agonists import get_glp1_agonists
from .claude.skills.search_nash_phase3_trials import search_nash_phase3_trials

# Use the functions
glp1_drugs = get_glp1_agonists()
nash_trials = search_nash_phase3_trials()
```

## Benefits (per Anthropic)

1. **Build Toolbox**: Accumulate higher-level capabilities over time
2. **Evolving Expertise**: Agent builds persistent knowledge across sessions
3. **Reusability**: Don't rewrite common query patterns
4. **Composability**: Combine functions to answer complex queries

## Example Function

```python
import sys
sys.path.insert(0, 'scripts')
from mcp.servers.fda_mcp import lookup_drug

def get_glp1_agonists():
    """Get all GLP-1 receptor agonists."""
    results = lookup_drug(
        search_term="GLP-1 receptor agonist",
        search_type="general",
        limit=50
    )

    brands = {}
    for result in results.get('data', {}).get('results', []):
        openfda = result.get('openfda', {})
        for brand in openfda.get('brand_name', []):
            generic = openfda.get('generic_name', ['Unknown'])[0]
            brands[brand] = generic
    return brands
```

## Key Characteristics

- **Focused**: Each function does one thing well
- **Documented**: Clear docstrings explain purpose
- **Importable**: Can be imported by future code executions
- **Self-contained**: Includes all necessary imports
- **Returns data**: Returns processed data structures (not print statements)

## Maintenance

- ✅ Functions added automatically by agent-generated code
- ✅ Each function saved immediately after successful execution
- ✅ No manual editing required
- ✅ Version controlled (.claude/skills/ tracked in git)
