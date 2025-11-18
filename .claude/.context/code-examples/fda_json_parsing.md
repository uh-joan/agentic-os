# FDA JSON Parsing Pattern

## When to Use This Example
- Query involves FDA drug/device data
- Need to parse drug labels, brand names, adverse events
- Server: `mcp.servers.fda_mcp`

## Critical: Response Format
**FDA returns JSON DICT, not string!**

## Complete Working Example

```python
import sys
sys.path.insert(0, 'scripts')
from pathlib import Path

from mcp.servers.fda_mcp import lookup_drug

# Reusable function
def get_glp1_obesity_drugs():
    """Get all GLP-1 drugs approved for obesity."""
    results = lookup_drug(
        search_term="GLP-1 receptor agonist obesity",
        search_type="general",
        limit=100
    )

    # FDA returns JSON dict - use .get() methods
    brands = {}
    for result in results.get('data', {}).get('results', []):
        openfda = result.get('openfda', {})
        for brand in openfda.get('brand_name', []):
            generic = openfda.get('generic_name', ['Unknown'])[0]
            brands[brand] = generic
    return brands

# Execute and display
brands = get_glp1_obesity_drugs()
print("GLP-1 Drugs Approved for Obesity:")
for brand, generic in sorted(brands.items()):
    print(f"  • {brand} ({generic})")
print(f"\nTotal: {len(brands)} products")

# Save to skills library
skill_path = Path('.claude/skills/get_glp1_obesity_drugs.py')
skill_path.parent.mkdir(parents=True, exist_ok=True)
skill_path.write_text('''import sys
sys.path.insert(0, "scripts")
from mcp.servers.fda_mcp import lookup_drug

def get_glp1_obesity_drugs():
    """Get all GLP-1 drugs approved for obesity."""
    results = lookup_drug(
        search_term="GLP-1 receptor agonist obesity",
        search_type="general",
        limit=100
    )
    brands = {}
    for result in results.get("data", {}).get("results", []):
        openfda = result.get("openfda", {})
        for brand in openfda.get("brand_name", []):
            generic = openfda.get("generic_name", ["Unknown"])[0]
            brands[brand] = generic
    return brands
''')

# Save SKILL.md
skill_md = Path('.claude/skills/get_glp1_obesity_drugs.md')
skill_md.write_text('''# get_glp1_obesity_drugs

## Purpose
Get all GLP-1 receptor agonist drugs approved for obesity.

## Returns
- `dict[str, str]`: Mapping of brand names to generic names

## Usage
\`\`\`python
from .claude.skills.get_glp1_obesity_drugs import get_glp1_obesity_drugs
brands = get_glp1_obesity_drugs()
\`\`\`

## MCP Tools Used
- fda_mcp.lookup_drug
''')
```

## Key Patterns

### 1. Parse JSON Response
```python
# FDA returns dict with nested structure
results = lookup_drug(...)
data = results.get('data', {})
items = data.get('results', [])
```

### 2. Extract OpenFDA Fields
```python
for result in results.get('data', {}).get('results', []):
    openfda = result.get('openfda', {})

    # Common fields:
    brands = openfda.get('brand_name', [])
    generics = openfda.get('generic_name', [])
    routes = openfda.get('route', [])
    manufacturers = openfda.get('manufacturer_name', [])
```

### 3. Handle Missing Data
```python
# Always provide defaults
generic = openfda.get('generic_name', ['Unknown'])[0]
brands = openfda.get('brand_name', [])  # Empty list if missing

# Check before accessing
if openfda.get('brand_name'):
    brand = openfda['brand_name'][0]
```

### 4. Common Data Extraction Patterns
```python
# Extract unique brand names
brands = set()
for result in results.get('data', {}).get('results', []):
    brands.update(result.get('openfda', {}).get('brand_name', []))

# Map brands to generics
brand_map = {}
for result in results.get('data', {}).get('results', []):
    openfda = result.get('openfda', {})
    for brand in openfda.get('brand_name', []):
        generic = openfda.get('generic_name', ['Unknown'])[0]
        brand_map[brand] = generic
```

## Parameter Reference
See `.claude/.context/mcp-tool-guides/fda.md` for full parameter list.

Common parameters:
- `search_term` - Drug name, condition, or keyword
- `search_type` - "general", "label", "adverse_events", "recalls"
- `limit` - Max results (default: 10, max: 100)
