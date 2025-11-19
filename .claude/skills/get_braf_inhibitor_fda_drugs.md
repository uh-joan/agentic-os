# get_braf_inhibitor_fda_drugs

Get FDA approved BRAF inhibitor drugs from the FDA drugs database.

## Purpose

Retrieves structured information about FDA-approved BRAF inhibitor drugs including brand names, generic names, application numbers, approval dates, and manufacturers.

## Data Source

- **MCP Server**: `fda_mcp`
- **Tool**: `search_drugs`
- **Search Term**: "BRAF inhibitor"
- **Response Format**: JSON

## Returns

```python
{
    'total_count': int,  # Number of unique drugs found
    'drugs': [
        {
            'brand_name': str,        # Brand name (e.g., "TAFINLAR")
            'generic_name': str,      # Generic name (e.g., "dabrafenib")
            'application_number': str, # FDA application number
            'approval_date': str,     # Approval date (YYYY-MM-DD)
            'manufacturer': str       # Manufacturer name
        },
        ...
    ]
}
```

## Usage

### As importable module:
```python
from .claude.skills.get_braf_inhibitor_fda_drugs import get_braf_inhibitor_fda_drugs

result = get_braf_inhibitor_fda_drugs()
print(f"Found {result['total_count']} BRAF inhibitor drugs")
for drug in result['drugs']:
    print(f"- {drug['brand_name']} ({drug['generic_name']})")
```

### As standalone script:
```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_braf_inhibitor_fda_drugs.py
```

## Implementation Notes

- **Deduplication**: Uses brand name or generic name as key to avoid duplicates
- **Sorting**: Results sorted by approval date (newest first)
- **Data extraction**: Handles both `openfda` and `products` fields
- **Error handling**: Returns structured error if API returns no results

## Example Output

```
Total drugs found: 3

1. TAFINLAR (dabrafenib)
   Application: NDA021806
   Approved: 2018-06-27
   Manufacturer: Novartis Pharmaceuticals Corporation

2. ZELBORAF (vemurafenib)
   Application: NDA202429
   Approved: 2017-09-12
   Manufacturer: Genentech, Inc.

3. BRAFTOVI (encorafenib)
   Application: NDA210496
   Approved: 2020-04-08
   Manufacturer: Array BioPharma Inc.
```

## Therapeutic Context

BRAF inhibitors target the BRAF V600E mutation found in melanoma and other cancers. The three FDA-approved drugs represent different generations and combination strategies in BRAF-targeted therapy.

## Created

2025-01-19

## Pattern

Follows FDA JSON parsing pattern from `.claude/.context/code-examples/fda_json_parsing.md`
