# get_kras_inhibitor_fda_drugs

## Purpose
Get all FDA approved KRAS inhibitor drugs from the FDA database.

KRAS inhibitors are targeted cancer therapies that inhibit KRAS mutations, particularly KRAS G12C mutations found in non-small cell lung cancer (NSCLC), colorectal cancer, and other solid tumors.

## Returns
- `dict[str, dict]`: Dictionary mapping brand names to drug information
  - Format: `{brand_name: {'generic': str, 'count': int}}`

## Current FDA Approved KRAS Inhibitors
As of execution date:
1. **LUMAKRAS** (sotorasib) - First-in-class KRAS G12C inhibitor
2. **KRAZATI** (adagrasib) - Second KRAS G12C inhibitor

## Usage
```python
from .claude.skills.get_kras_inhibitor_fda_drugs import get_kras_inhibitor_fda_drugs

# Get all KRAS inhibitors
kras_drugs = get_kras_inhibitor_fda_drugs()

# Display results
for brand, info in kras_drugs.items():
    print(f"{brand} ({info['generic']})")
```

## MCP Tools Used
- `fda_mcp.lookup_drug` - FDA drug database query

## Search Strategy
The function uses a two-pronged approach:
1. **Broad search**: Attempts "KRAS inhibitor" term (may not return results)
2. **Specific search**: Searches known KRAS inhibitor drug names (sotorasib, adagrasib, LUMAKRAS, KRAZATI)

This hybrid approach ensures robust drug discovery even if FDA API doesn't support broad mechanism terms.

## Clinical Context
KRAS mutations were historically considered "undruggable" until the development of covalent KRAS G12C inhibitors. These drugs represent a major breakthrough in precision oncology.

**Target mutation**: KRAS G12C
**Primary indication**: NSCLC (non-small cell lung cancer)
**Other indications**: Colorectal cancer, pancreatic cancer (under investigation)

## Related Skills
- `get_kras_clinical_trials` - Active KRAS inhibitor trials
- `get_kras_patents` - KRAS inhibitor patent landscape
