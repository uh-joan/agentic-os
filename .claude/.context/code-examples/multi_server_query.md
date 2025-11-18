# Multi-Server Query Pattern

## When to Use This Example
- Query requires data from multiple MCP servers
- Need to combine FDA + CT.gov data
- Cross-reference different data sources

## Complete Working Example

```python
import sys
import re
sys.path.insert(0, 'scripts')

from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.ct_gov_mcp import search

# Query 1: Get approved obesity drugs from FDA
print("Querying FDA for approved obesity drugs...")
fda_results = lookup_drug(
    search_term="obesity",
    search_type="general",
    limit=100
)

# Extract approved drugs (FDA returns JSON)
approved_drugs = set()
for result in fda_results.get('data', {}).get('results', []):
    openfda = result.get('openfda', {})
    approved_drugs.update(openfda.get('generic_name', []))

print(f"Found {len(approved_drugs)} approved obesity drugs")

# Query 2: Get recruiting trials from CT.gov
print("Querying ClinicalTrials.gov for Phase 3 trials...")
ct_result = search(
    condition="obesity",
    phase="PHASE3",
    status="recruiting",
    location="United States",
    pageSize=10
)

# Extract count (CT.gov returns markdown)
trial_count = 0
if isinstance(ct_result, str):
    match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', ct_result)
    if match:
        trial_count = int(match.group(1))

print(f"Found {trial_count} Phase 3 trials recruiting")

# Summary
print("\n" + "=" * 60)
print("OBESITY DRUG LANDSCAPE SUMMARY")
print("=" * 60)
print(f"Approved drugs (FDA):          {len(approved_drugs)}")
print(f"Phase 3 trials recruiting:     {trial_count}")
print(f"Pipeline activity:             {'Strong' if trial_count > 20 else 'Moderate'}")
print("\nTop approved drugs:")
for drug in sorted(approved_drugs)[:5]:
    print(f"  • {drug}")
```

## Key Patterns

### 1. Import Multiple Servers
```python
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.ct_gov_mcp import search
from mcp.servers.pubmed_mcp import search_keywords
```

### 2. Handle Different Response Formats
```python
# FDA returns JSON
fda_result = lookup_drug(...)
fda_data = fda_result.get('data', {}).get('results', [])

# CT.gov returns markdown string
ct_result = search(...)
if isinstance(ct_result, str):
    match = re.search(r'pattern', ct_result)

# PubMed returns JSON
pubmed_result = search_keywords(...)
articles = pubmed_result.get('articles', [])
```

### 3. Cross-Reference Data
```python
# Example: Find trials for approved drugs
approved_drugs = set(['semaglutide', 'liraglutide'])

for drug in approved_drugs:
    ct_result = search(
        intervention=drug,
        phase="PHASE3",
        pageSize=10
    )
    # Process each drug's trials...
```

### 4. Aggregate Results
```python
# Collect data from multiple queries
all_results = {
    'fda': {},
    'ct_gov': {},
    'pubmed': {}
}

# FDA query
fda_data = lookup_drug(...)
all_results['fda']['brands'] = extract_brands(fda_data)

# CT.gov query
ct_data = search(...)
all_results['ct_gov']['trial_count'] = parse_count(ct_data)

# Combine for final summary
print(f"Total drugs: {len(all_results['fda']['brands'])}")
print(f"Total trials: {all_results['ct_gov']['trial_count']}")
```

## Performance Tips

### 1. Query in Parallel Conceptually
```python
# All queries are independent - can be executed sequentially
# MCP client handles them efficiently
fda_result = lookup_drug(...)
ct_result = search(...)
pubmed_result = search_keywords(...)
```

### 2. Process Data In-Memory
```python
# ✅ GOOD: Process all data in code
brands = set()
for result in fda_results.get('data', {}).get('results', []):
    brands.update(result.get('openfda', {}).get('brand_name', []))

# Only print summary
print(f"Found {len(brands)} brands")

# ❌ BAD: Don't print raw data
# print(json.dumps(fda_results))  # Wastes tokens!
```

### 3. Filter Early
```python
# Filter as you extract
relevant_drugs = []
for result in fda_results.get('data', {}).get('results', []):
    # Only keep drugs with specific criteria
    if meets_criteria(result):
        relevant_drugs.append(result)
```

## Example Use Cases

### Compare Approved Drugs vs Pipeline
```python
approved = get_fda_approved_drugs("obesity")
pipeline = get_ctgov_trial_count("obesity", "PHASE3")
print(f"Market: {len(approved)} drugs")
print(f"Pipeline: {pipeline} trials")
```

### Find Trials for Specific Drug
```python
drug_name = "semaglutide"
fda_data = lookup_drug(search_term=drug_name)
ct_data = search(intervention=drug_name)
# Cross-reference...
```

### Literature + Trials Analysis
```python
pubmed_articles = search_keywords(keywords="GLP-1 obesity")
ct_trials = search(condition="obesity", intervention="GLP-1")
# Combine insights...
```
