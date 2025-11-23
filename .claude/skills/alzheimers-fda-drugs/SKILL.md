---
name: get_alzheimers_fda_drugs
description: Get FDA approved Alzheimer's disease drugs with deduplication and detailed information
category: drug-discovery
servers:
  - fda_mcp
patterns:
  - fda_json_parsing
  - drug_deduplication
  - metadata_extraction
complexity: simple
created: 2025-11-23
---

# FDA Approved Alzheimer's Disease Drugs

Comprehensive collection of all FDA-approved drugs for Alzheimer's disease, including
cholinesterase inhibitors, NMDA receptor antagonists, and newer anti-amyloid antibodies.

## Function Signature

```python
get_alzheimers_fda_drugs() -> dict
```

## Returns

Dictionary containing:
- `drugs`: List of unique drug information dictionaries
- `total_count`: Total number of unique approved drugs
- `drugs_by_class`: Breakdown by mechanism class
- `summary`: Formatted summary string

## Drug Classes Covered

- Cholinesterase inhibitors (donepezil, rivastigmine, galantamine)
- NMDA receptor antagonists (memantine)
- Anti-amyloid antibodies (aducanumab, lecanemab, donanemab)
- Combination therapies

## Usage

```python
from claude.skills.alzheimers_fda_drugs.scripts.get_alzheimers_fda_drugs import get_alzheimers_fda_drugs

result = get_alzheimers_fda_drugs()
print(result['summary'])
print(f"Total approved drugs: {result['total_count']}")
```
