# MCP Alternative Methods - User Guide

## Overview

This directory contains **client-side alternative functions** that bypass broken or problematic MCP methods by calling REST APIs directly with proper field selection and filtering.

**Why these alternatives exist:**
- Some MCP methods return responses that exceed the 25,000 token MCP limit
- Some MCP methods return errors (400 bad request)
- These alternatives provide the same functionality with token-efficient implementations

---

## Critical Bugs & Alternatives

### 1. PubChem get_safety_data (CRITICAL BUG)

**Problem:**
- Returns 21.9 MILLION tokens
- Exceeds MCP limit by 876x
- Query will ALWAYS FAIL

**Alternative:** `pubchem_mcp/alternatives.py`

```python
from scripts.mcp.servers.pubchem_mcp.alternatives import (
    get_safety_data_alternative,
    get_ghs_classification_summary
)

# Get safety data with section filtering (500-2,000 tokens)
safety = get_safety_data_alternative(
    cid="2244",  # Aspirin
    fields=['GHS Classification', 'Hazards', 'Precautions']
)

# Get minimal GHS codes only (200-500 tokens)
ghs = get_ghs_classification_summary(cid="2244")
print(ghs['ghs_codes'])  # ['H302', 'H318', ...]
```

**Token savings:** 99.998% (21.9M → 500-2,000 tokens)

---

### 2. PubChem search_similar_compounds (BROKEN)

**Problem:**
- Returns 400 bad request error
- Method does not work at all

**Alternative:** `pubchem_mcp/alternatives.py`

```python
from scripts.mcp.servers.pubchem_mcp.alternatives import (
    search_similar_compounds_alternative
)

# Search for compounds similar to aspirin
results = search_similar_compounds_alternative(
    smiles="CC(=O)Oc1ccccc1C(=O)O",  # Aspirin SMILES
    threshold=90,
    max_records=10
)

# Results include CID, formula, weight, IUPAC name
for compound in results['compounds']:
    print(f"{compound['CID']}: {compound['MolecularFormula']}")
```

**Token usage:** ~100-500 tokens per compound (reasonable)

---

### 3. FDA Label Queries (CRITICAL BUG)

**Problem:**
- Returns 110,112 tokens for single drug label
- Exceeds MCP limit by 4.4x
- Query will ALWAYS FAIL

**Alternative:** `fda_mcp/alternatives.py`

```python
from scripts.mcp.servers.fda_mcp.alternatives import (
    get_drug_label_alternative,
    get_label_sections_summary
)

# Get essential label sections only (500-1,000 tokens)
label = get_label_sections_summary(search_term="aspirin")

# Get specific sections you need (2,000-5,000 tokens)
label = get_drug_label_alternative(
    search_term="aspirin",
    fields=[
        'indications_and_usage',
        'warnings',
        'contraindications',
        'dosage_and_administration',
        'adverse_reactions'
    ]
)

# Get comprehensive label (still under 10k tokens)
label = get_drug_label_alternative(
    search_term="aspirin",
    fields=[
        'openfda.brand_name',
        'openfda.generic_name',
        'indications_and_usage',
        'warnings',
        'contraindications',
        'adverse_reactions',
        'drug_interactions',
        'dosage_and_administration',
        'clinical_pharmacology',
        'boxed_warning'
    ]
)
```

**Token savings:** 95.5% (110k → 2-5k tokens)

---

### 4. FDA Adverse Events (OPTIMIZATION)

**Problem:**
- Without count parameter: 67,000 tokens (exceeds limit by 2.7x)
- With count parameter: 150-400 tokens

**Alternative:** `fda_mcp/alternatives.py`

```python
from scripts.mcp.servers.fda_mcp.alternatives import (
    get_adverse_events_summary
)

# Get top reactions for a drug (200-500 tokens)
events = get_adverse_events_summary(drug_name="aspirin")

# Get serious event breakdown
events = get_adverse_events_summary(
    drug_name="aspirin",
    count_field="serious"
)

# Get adverse events by country
events = get_adverse_events_summary(
    drug_name="aspirin",
    count_field="occurcountry.exact"
)
```

**Token usage:** ~200-500 tokens (always efficient)

---

### 5. FDA Search by Indication

**Additional utility for finding drugs by condition:**

```python
from scripts.mcp.servers.fda_mcp.alternatives import (
    search_drugs_by_indication
)

# Find drugs approved for hypertension
drugs = search_drugs_by_indication(
    indication="hypertension",
    limit=10
)

# Results include brand name, generic name, manufacturer, indication snippet
for drug in drugs['drugs']:
    print(f"{drug['brand_name']} ({drug['generic_name']})")
```

**Token usage:** ~1,000-3,000 tokens

---

## Usage Patterns

### Pattern 1: Replace Broken MCP Call

**Before (broken):**
```python
# This will FAIL - returns 21.9M tokens
result = mcp__pubchem_mcp_server__pubchem(
    method="get_safety_data",
    cid="2244"
)
```

**After (working):**
```python
from scripts.mcp.servers.pubchem_mcp.alternatives import get_safety_data_alternative

# This works - returns 500-2,000 tokens
result = get_safety_data_alternative(
    cid="2244",
    fields=['GHS Classification', 'Hazards']
)
```

### Pattern 2: Field Selection for Token Efficiency

**Before (inefficient):**
```python
# Returns 110k tokens - FAILS
label = mcp__fda_mcp__fda_info(
    method="lookup_drug",
    search_type="label",
    search_term="aspirin"
)
```

**After (efficient):**
```python
from scripts.mcp.servers.fda_mcp.alternatives import get_drug_label_alternative

# Returns 2-5k tokens - succeeds
label = get_drug_label_alternative(
    search_term="aspirin",
    fields=[
        'indications_and_usage',
        'warnings',
        'dosage_and_administration'
    ]
)
```

### Pattern 3: Minimal Data for Quick Lookups

**Use case:** Just need GHS codes, not full safety data

```python
from scripts.mcp.servers.pubchem_mcp.alternatives import get_ghs_classification_summary

# Ultra-efficient: 200-500 tokens
ghs = get_ghs_classification_summary(cid="2244")

# Just the codes
hazard_codes = ghs['ghs_codes']  # ['H302', 'H318', ...]
```

---

## Available FDA Label Fields

When using `get_drug_label_alternative()`, you can select from these fields:

### Essential (always recommended):
- `openfda.brand_name`
- `openfda.generic_name`
- `openfda.manufacturer_name`
- `indications_and_usage`
- `warnings`
- `contraindications`
- `dosage_and_administration`
- `adverse_reactions`

### Additional (add if needed):
- `boxed_warning` - Black box warnings
- `warnings_and_cautions` - Detailed warnings
- `drug_interactions` - Drug-drug interactions
- `use_in_specific_populations` - Special populations
- `clinical_pharmacology` - Mechanism of action
- `mechanism_of_action` - How the drug works
- `description` - Chemical description
- `clinical_studies` - Clinical trial data
- `information_for_patients` - Patient counseling
- `pediatric_use` - Pediatric information
- `geriatric_use` - Geriatric information
- `pregnancy` - Pregnancy category

### Strategy:
1. Start with essential fields only (500-1,000 tokens)
2. Add specific fields you need (2,000-5,000 tokens)
3. Never request all fields (will exceed token limit)

---

## Available PubChem Safety Fields

When using `get_safety_data_alternative()`, you can select from these sections:

- `GHS Classification` - Hazard classification codes
- `Hazards` - Hazard statements
- `Precautions` - Precautionary statements
- `Safety and Hazards` - General safety info
- `Toxicity` - Toxicological data
- `Handling and Storage` - Storage conditions
- `Disposal` - Disposal methods
- `Fire Fighting` - Fire response
- `First Aid` - First aid measures

**Default:** `['GHS Classification', 'Hazards', 'Precautions']` (most commonly needed)

---

## Performance Comparison

| Method | Original MCP | Alternative | Token Savings |
|--------|--------------|-------------|---------------|
| PubChem safety data | 21,900,000 | 500-2,000 | 99.998% |
| PubChem similarity | 400 error | 100-500 | Fixed + efficient |
| FDA label query | 110,112 | 2,000-5,000 | 95.5% |
| FDA adverse events | 67,000 | 200-500 | 99.3% |

---

## Integration with pharma-search-specialist

The pharma-search-specialist agent can use these alternatives automatically:

```json
{
  "execution_plan": [
    {
      "step": 1,
      "description": "Get aspirin safety data using alternative",
      "tool": "Python",
      "method": "execute",
      "code": "from scripts.mcp.servers.pubchem_mcp.alternatives import get_safety_data_alternative\nresult = get_safety_data_alternative(cid='2244', fields=['GHS Classification', 'Hazards'])",
      "token_budget": 2000
    }
  ]
}
```

---

## Error Handling

All alternative functions return error information on failure:

```python
result = get_drug_label_alternative(search_term="invalid_drug_xyz")

if 'error' in result:
    print(f"Error: {result['message']}")
    print(f"Details: {result['error']}")
else:
    # Process successful result
    print(result['results'])
```

---

## Best Practices

1. **Always use alternatives for known broken methods**
   - PubChem get_safety_data → use get_safety_data_alternative()
   - PubChem search_similar_compounds → use search_similar_compounds_alternative()
   - FDA label queries → use get_drug_label_alternative()

2. **Use minimal field selection**
   - Request only the fields you actually need
   - Start with essential fields, add more if needed
   - Monitor token estimates in responses

3. **Check token estimates**
   - All alternatives return `token_estimate` field
   - Use this to validate you're under the 25k limit
   - Reduce fields if estimate is too high

4. **Handle errors gracefully**
   - Check for 'error' key in response
   - Have fallback strategies
   - Log failures for debugging

5. **Document your usage**
   - Note which alternative you used
   - Save raw results to data_dump/
   - Include token measurements in documentation

---

## Future Alternatives

Additional alternatives may be created for:
- DataCommons search_indicators (currently 7,500 tokens - verbose but not failing)
- Any new methods discovered to exceed token limits

---

## Support

For issues with alternatives:
1. Check that you have `requests` library installed: `pip install requests`
2. Verify your query parameters are correct
3. Check network connectivity to FDA/PubChem APIs
4. Review error messages in response

For MCP server bugs:
- Report to MCP server maintainers
- Reference CRITICAL_BUGS_ANALYSIS.md for details
- Suggest implementing field selection parameters

---

## Files

- `pubchem_mcp/alternatives.py` - PubChem workarounds (3 functions)
- `fda_mcp/alternatives.py` - FDA workarounds (4 functions)
- `ALTERNATIVES_README.md` - This documentation

**Total alternatives:** 7 functions protecting users from 3 critical bugs
