---
name: get_glp1_diabetes_drugs
description: >
  Get GLP-1 drugs specifically for diabetes indication from FDA database. Filters by diabetes indication to distinguish from obesity-focused GLP-1s. Use when analyzing diabetes therapeutics market or indication-specific development. Keywords: GLP-1, diabetes, type 2 diabetes, FDA approval, diabetes drugs.
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - fda_json_parsing
  - indication_filtering
data_scope:
  total_results: varies
  geographical: US
  temporal: All time
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_glp1_diabetes_drugs

**Category**: FDA Drug Information
**MCP Server**: fda_mcp
**Created**: 2025-01-18

## Purpose

Query FDA database for GLP-1 receptor agonist drugs approved for Type 2 Diabetes treatment.

## Function Signature

```python
def get_glp1_diabetes_drugs() -> dict
```

## Returns

```python
{
    "count": int,  # Number of drugs found
    "drugs": [     # List of drug information dicts
        {
            "brand_names": list,      # Brand names (e.g., ["OZEMPIC"])
            "generic_names": list,    # Generic names (e.g., ["SEMAGLUTIDE"])
            "manufacturer": list,     # Manufacturer names
            "indications": list,      # Indications and usage
            "approval_date": list     # Approval dates
        }
    ]
}
```

## Example Usage

```python
from .claude.skills.glp1_diabetes_drugs.scripts.get_glp1_diabetes_drugs import get_glp1_diabetes_drugs

# Get all GLP-1 diabetes drugs
results = get_glp1_diabetes_drugs()

print(f"Found {results['count']} GLP-1 drugs")

for drug in results['drugs']:
    brand = drug['brand_names'][0] if drug['brand_names'] else 'N/A'
    generic = drug['generic_names'][0] if drug['generic_names'] else 'N/A'
    print(f"{brand} ({generic})")
```

## MCP Tool Used

- `mcp__fda_mcp__fda_info`
  - `search_term`: "GLP-1 receptor agonist"
  - `indication`: "diabetes"

## Response Format

FDA returns JSON with nested structure:
- `results[]` - Array of drug records
  - `openfda{}` - OpenFDA metadata
    - `brand_name[]` - Brand names
    - `generic_name[]` - Generic names
    - `manufacturer_name[]` - Manufacturers
    - `approval_date[]` - Approval dates
  - `indications_and_usage[]` - Usage information

## Pattern Demonstrated

- ✅ FDA JSON parsing with `.get()` methods
- ✅ Extracting nested OpenFDA metadata
- ✅ Handling list fields safely
- ✅ Returning structured data for reuse
- ✅ In-memory processing (no file output)

## Related Skills

- `get_glp1_obesity_drugs.py` - GLP-1 drugs for obesity indication
- Future: `compare_glp1_diabetes_obesity.py` - Cross-indication comparison

## Notes

- GLP-1 receptor agonists are a drug class used for Type 2 Diabetes and obesity
- FDA database includes brand names, generic names, and approval metadata
- Multiple brand names may exist for same generic drug
- Response format is JSON (not markdown - see CT.gov for markdown responses)
