# get_glp1_fda_drugs

Get FDA approved GLP-1 receptor agonist drugs with comprehensive information.

## Purpose

Collects FDA approval data for all major GLP-1 receptor agonists including:
- Semaglutide (Ozempic, Wegovy, Rybelsus)
- Tirzepatide (Mounjaro, Zepbound)
- Liraglutide (Victoza, Saxenda)
- Dulaglutide (Trulicity)
- Exenatide (Byetta, Bydureon)
- Albiglutide
- Lixisenatide

## Function Signature

```python
def get_glp1_fda_drugs() -> dict:
    """Get FDA approved GLP-1 receptor agonist drugs.

    Returns:
        dict: {
            'drugs': list[dict],        # List of drug information dicts
            'total_count': int,          # Number of unique drugs
            'summary': str               # Formatted summary string
        }
    """
```

## Return Structure

Each drug dict contains:
- `active_ingredient`: Generic drug name
- `brand_name`: Commercial name
- `manufacturer`: Company name
- `approval_date`: FDA approval date (YYYY-MM-DD)
- `dosage_form`: Injection, tablet, etc.
- `route`: Administration route
- `application_number`: FDA application number
- `indications`: First 200 chars of indications/usage

## Usage

### As Import
```python
from .claude.skills.get_glp1_fda_drugs import get_glp1_fda_drugs

result = get_glp1_fda_drugs()
print(f"Found {result['total_count']} GLP-1 drugs")
for drug in result['drugs']:
    print(f"{drug['brand_name']} - {drug['active_ingredient']}")
```

### As Standalone
```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_glp1_fda_drugs.py
```

## Data Source

- **MCP Server**: `fda_mcp`
- **API**: FDA Drug Labels API
- **Search Method**: Brand name search for each GLP-1 active ingredient

## Notes

- Removes duplicate entries based on application_number
- Sorts by approval_date (most recent first)
- Handles missing data gracefully with 'Unknown' defaults
- Truncates long indications text to 200 characters
- Searches up to 10 results per drug name to capture all formulations

## Last Updated

2025-01-19
