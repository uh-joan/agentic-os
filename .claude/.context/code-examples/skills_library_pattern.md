# Skills Library Pattern (Folder Structure)

## When to Use This Example
- Every query! Always save reusable functions to skills library
- Following Anthropic's code execution pattern + folder structure
- Building persistent expertise across sessions

## Why Skills Library?

From Anthropic's article:
> "Skills Library: Save reusable functions to build a toolbox of higher-level capabilities over time"

**Benefits**:
- Future queries can import and reuse functions
- Agent builds expertise across sessions
- Reduces duplicate code generation
- Creates composable building blocks
- **Folder structure**: Self-contained, shareable packages
- **YAML frontmatter**: Standardized metadata for discovery

## Complete Pattern (Folder Structure - v2.0)

**Agent executes code and returns folder structure to main agent**:

### 1. Define and Execute Function

```python
import sys
sys.path.insert(0, 'scripts')
from mcp.servers.fda_mcp import lookup_drug

# Define reusable function
def search_drug_brands(search_term, limit=100):
    """Reusable function to search drug brands."""
    results = lookup_drug(search_term=search_term, limit=limit)

    brands = set()
    for result in results.get('data', {}).get('results', []):
        openfda = result.get('openfda', {})
        brands.update(openfda.get('brand_name', []))
    return brands

# Execute and display
brands = search_drug_brands("obesity", limit=50)
print(f"Found {len(brands)} brands")
for brand in sorted(brands)[:10]:
    print(f"  • {brand}")
```

### 2. Agent Returns Folder Structure to Main Agent

**DO NOT use Path.write_text() in agent code**. Instead, return the skill in your response:

```
Found 21 brands for obesity drugs.

Skill folder: drug-brands-search/

SKILL.md:
\```markdown
---
name: search_drug_brands
description: >
  Search FDA database for drug brands by search term with deduplication.
  Returns unique brand names. Use when analyzing drug markets, competitive
  landscapes, or brand portfolios. Keywords: FDA drugs, brand names, drug search.
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - fda_json_parsing
  - drug_deduplication
data_scope:
  total_results: varies
  geographical: US
  temporal: All time
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction
---

# search_drug_brands

## Purpose
Search FDA database for drug brands matching a search term.

## Parameters
- `search_term` (str): Search term for FDA lookup
- `limit` (int, optional): Maximum results (default: 100)

## Returns
- `set[str]`: Set of unique brand names

## Usage
\```python
from .claude.skills.drug_brands_search.scripts.search_drug_brands import search_drug_brands
brands = search_drug_brands("obesity", limit=50)
\```

## MCP Tools Used
- fda_mcp.lookup_drug
\```

Python script (scripts/search_drug_brands.py):
\```python
import sys
sys.path.insert(0, "scripts")
from mcp.servers.fda_mcp import lookup_drug

def search_drug_brands(search_term, limit=100):
    \"\"\"Reusable function to search drug brands.\"\"\"
    results = lookup_drug(search_term=search_term, limit=limit)
    brands = set()
    for result in results.get("data", {}).get("results", []):
        openfda = result.get("openfda", {})
        brands.update(openfda.get("brand_name", []))
    return brands

if __name__ == "__main__":
    brands = search_drug_brands("obesity", limit=50)
    print(f"Found {len(brands)} brands")
    for brand in sorted(brands)[:10]:
        print(f"  • {brand}")
\```
```

### 3. Main Agent Saves Files

Main Claude Code agent extracts and saves:

```python
# Main agent creates folder structure
skill_folder = Path('.claude/skills/drug-brands-search')
skill_folder.mkdir(parents=True, exist_ok=True)
(skill_folder / 'scripts').mkdir(exist_ok=True)

# Save SKILL.md (extracted from markdown block)
(skill_folder / 'SKILL.md').write_text(skill_md_content)

# Save Python script (extracted from python block)
(skill_folder / 'scripts' / 'search_drug_brands.py').write_text(python_content)
```

## OLD Pattern (Flat Structure - v1.0 Deprecated)

```python
sys.path.insert(0, "scripts")
from mcp.servers.fda_mcp import lookup_drug

def search_drug_brands(search_term, limit=100):
    """Reusable function to search drug brands."""
    results = lookup_drug(search_term=search_term, limit=limit)
    brands = set()
    for result in results.get("data", {}).get("results", []):
        openfda = result.get("openfda", {})
        brands.update(openfda.get("brand_name", []))
    return brands
''')

# 4. Save SKILL.md documentation
skill_md = Path('.claude/skills/search_drug_brands.md')
skill_md.write_text('''# search_drug_brands

## Purpose
Search for drug brands by search term.

## Parameters
- `search_term` (str): Search term for FDA lookup
- `limit` (int, optional): Maximum results (default: 100)

## Returns
- `set[str]`: Set of unique brand names

## Usage
\`\`\`python
from .claude.skills.drug_brands_search.scripts.search_drug_brands import search_drug_brands
brands = search_drug_brands("obesity", limit=50)
\`\`\`

## MCP Tools Used
- fda_mcp.lookup_drug

## Example Output
```
{'WEGOVY', 'OZEMPIC', 'SAXENDA', 'VICTOZA', 'RYBELSUS'}
```
''')

print("\n✓ Skill saved to .claude/skills/search_drug_brands.py")
```

## Skills Library Structure

```
.claude/skills/
├── search_drug_brands.py              # Function implementation
├── search_drug_brands.md              # Documentation
├── get_glp1_obesity_drugs.py
├── get_glp1_obesity_drugs.md
├── get_us_phase3_obesity_trials.py
└── get_us_phase3_obesity_trials.md
```

## Key Patterns

### 1. Always Use This Template

```python
from pathlib import Path

# Define function
def my_skill_function():
    # Implementation
    pass

# Execute
result = my_skill_function()
print(f"Result: {result}")

# Save .py file
skill_path = Path('.claude/skills/my_skill_function.py')
skill_path.parent.mkdir(parents=True, exist_ok=True)
skill_path.write_text('''[function code]''')

# Save .md file
skill_md = Path('.claude/skills/my_skill_function.md')
skill_md.write_text('''[documentation]''')
```

### 2. Function Naming Convention

```python
# ✅ GOOD: Descriptive, verb-based names
def get_glp1_obesity_drugs()
def search_nash_phase3_trials()
def count_recruiting_trials()

# ❌ BAD: Generic or unclear
def query()
def get_data()
def process()
```

### 3. SKILL.md Template

```markdown
# function_name

## Purpose
[One-line description of what this function does]

## Parameters
- `param1` (type): Description
- `param2` (type, optional): Description (default: value)

## Returns
- `type`: Description of return value

## Usage
\`\`\`python
from .claude.skills.skill_folder_name.scripts.function_name import function_name
result = function_name(arg1, arg2)
\`\`\`

## MCP Tools Used
- server_name.tool_name

## Example Output
\`\`\`
[Example of what the function returns]
\`\`\`

## Notes
[Any important notes about usage, quirks, limitations]
```

### 4. String Escaping in write_text()

**CRITICAL**: When saving Python code with regex, escape backslashes!

```python
# In the executing code (no extra escaping needed)
match = re.search(r'\*\*Results:\*\* \d+ of (\d+)', result)

# In write_text() - DOUBLE the backslashes
skill_path.write_text('''import re

def my_function():
    match = re.search(r"\\\\*\\\\*Results:\\\\*\\\\* \\\\d+ of (\\\\d+)", result)
    # Each \\ becomes \ in the saved file
''')
```

## Reusing Skills

### Future Query Example

```python
# Instead of re-implementing, import existing skills (folder structure)
from .claude.skills.drug_brands_search.scripts.search_drug_brands import search_drug_brands
from .claude.skills.us_phase3_obesity_recruiting_trials.scripts.get_us_phase3_obesity_recruiting_trials import get_us_phase3_obesity_recruiting_trials

# Use them
obesity_brands = search_drug_brands("obesity")
trial_count = get_us_phase3_obesity_recruiting_trials()

print(f"Obesity market: {len(obesity_brands)} brands")
print(f"Pipeline: {trial_count} Phase 3 trials")
```

## Agent Discovery

Agent can read SKILL.md files to discover available skills:

```python
# Agent checks what skills exist
skill_files = Path('.claude/skills').glob('*.md')
for skill_file in skill_files:
    # Read documentation to understand what's available
    doc = skill_file.read_text()
    # Decide if relevant to current query
```

## Best Practices

### 1. Keep Functions Focused
```python
# ✅ GOOD: Single responsibility
def get_trial_count(condition, phase):
    # Just returns count
    return count

# ❌ BAD: Does too much
def get_trials_and_analyze_and_compare():
    # Too complex for reuse
```

### 2. Make Functions Parameterized
```python
# ✅ GOOD: Flexible, reusable
def search_trials(condition, phase, status="recruiting"):
    # Can be used for different conditions/phases

# ❌ BAD: Hardcoded
def search_obesity_phase3_trials():
    # Only works for obesity + phase 3
```

### 3. Include Error Handling
```python
def safe_search(condition):
    try:
        result = search(condition=condition)
        return parse_result(result)
    except Exception as e:
        print(f"Error: {e}")
        return 0  # Sensible default
```

### 4. Always Save Both .py and .md
- `.py` = importable function
- `.md` = documentation for agent discovery

Both files must have the same base name!
