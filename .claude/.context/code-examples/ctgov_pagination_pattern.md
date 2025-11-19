# CT.gov Pagination Pattern

**Source**: Extracted from `get_glp1_trials.py` (production-validated, retrieves 1803/1803 trials)
**Use case**: Any CT.gov search potentially returning >1000 results
**Critical**: Without pagination, you only get 55% of data (1000/1803 trials)

## Problem

ClinicalTrials.gov API returns maximum **1000 results per page**. Queries with more results require pagination to collect complete datasets.

**Real example**:
- GLP-1 trials: 1803 total in database
- Without pagination: Get only 1000 trials (55% of data)
- With pagination: Get all 1803 trials across 2 pages (100% of data)

## Solution Pattern

### Complete Pagination Implementation

```python
import sys
import re
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_trials_with_pagination(search_term):
    """Get clinical trials with full pagination support.

    Returns:
        dict: Contains total_count, trials_parsed, and summary
    """

    all_trials = []
    page_token = None
    page_count = 0
    total_count = 0

    # Paginate through all results
    while True:
        page_count += 1

        # Search with pagination token (None on first call)
        result = search(
            intervention=search_term,  # Or condition, phase, etc.
            pageSize=1000,             # Maximum page size
            pageToken=page_token       # None for first page, token for subsequent pages
        )

        # Extract total count from first page only
        if page_count == 1:
            total_match = re.search(r'\*\*Results:\*\*\s+([\d,]+)\s+of\s+([\d,]+)\s+studies found', result)
            if total_match:
                total_count = int(total_match.group(2).replace(',', ''))
            else:
                # Fallback: count NCT IDs in response
                total_count = len(re.findall(r'###\s+\d+\.\s+NCT\d{8}', result))

        # Parse trials from this page
        trial_sections = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)[1:]  # Skip header
        nct_ids = re.findall(r'###\s+\d+\.\s+(NCT\d{8})', result)

        for nct_id, section in zip(nct_ids, trial_sections):
            trial = {'nct_id': nct_id}

            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|\*\*)', section)
            if title_match:
                trial['title'] = title_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|\*\*)', section)
            if status_match:
                trial['status'] = status_match.group(1).strip()

            all_trials.append(trial)

        # Check for next page token
        # CT.gov API format: `pageToken: "TOKEN_STRING"`
        next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            page_token = next_token_match.group(1).strip()
            print(f"  Page {page_count} complete: {len(nct_ids)} trials. Fetching next page...")
        else:
            # No more pages
            print(f"  Page {page_count} complete: {len(nct_ids)} trials. No more pages.")
            break

    return {
        'total_count': total_count,
        'trials_parsed': all_trials,
        'pages_fetched': page_count
    }
```

## Key Implementation Details

### 1. Token Extraction
**Format in CT.gov response**:
```
To get the next page, use: `pageToken: "ZVNj7o2Elu8o3lpsCN675e3umpOQJJxtZPem2PMekA"`
```

**Regex pattern**:
```python
next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
```

**Explanation**:
- `` ` `` - Match literal backtick
- `pageToken:\s*` - Match "pageToken:" with optional whitespace
- `"([^"]+)"` - Capture everything between quotes (the token)

### 2. Pagination Loop Logic

```python
page_token = None  # Start with None for first page

while True:
    # Make API call
    result = search(..., pageToken=page_token)

    # Process results
    # ...

    # Check for next page
    next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
    if next_token_match:
        page_token = next_token_match.group(1).strip()  # Extract token for next iteration
    else:
        break  # No more pages - exit loop
```

### 3. Page Size Maximum
```python
pageSize=1000  # Maximum allowed by CT.gov API
```

**Note**: FDA API maximum is different (100). Always check MCP tool guides for server-specific limits.

### 4. Progress Reporting
```python
print(f"  Page {page_count} complete: {len(nct_ids)} trials. Fetching next page...")
```

**Benefits**:
- User feedback for long-running queries
- Debugging visibility
- Progress tracking

## Real-World Results

**GLP-1 trials example**:
```
Page 1 complete: 1000 trials. Fetching next page...
Page 2 complete: 803 trials. No more pages.

Total: 1803/1803 trials retrieved (100%)
```

**Without pagination**:
```
Retrieved: 1000/1803 trials (55%)
Missing: 803 trials (45% of data)
```

## When to Use This Pattern

✅ **Use pagination when**:
- Query might return >1000 results
- Broad search terms (e.g., "GLP-1", "diabetes", "cancer")
- Therapeutic area queries
- Unknown result count

❌ **Pagination not needed when**:
- Specific NCT ID lookup (single result)
- Highly filtered queries (status + phase + location + sponsor)
- Result count known to be <1000

## Common Mistakes to Avoid

### Mistake 1: Wrong regex pattern
```python
# ❌ Wrong - looks for **nextPageToken:**
next_token_match = re.search(r'\*\*nextPageToken:\*\*\s*(\S+)', result)

# ✅ Correct - matches actual format
next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
```

### Mistake 2: Not initializing page_token to None
```python
# ❌ Wrong - undefined variable
while True:
    result = search(..., pageToken=page_token)  # Error on first iteration

# ✅ Correct - initialize before loop
page_token = None
while True:
    result = search(..., pageToken=page_token)  # Works - None means first page
```

### Mistake 3: Extracting total count on every page
```python
# ❌ Inefficient - parses total count on every page
while True:
    result = search(...)
    total_match = re.search(r'Results:\*\*\s+([\d,]+)\s+of\s+([\d,]+)', result)
    total_count = int(total_match.group(2).replace(',', ''))

# ✅ Efficient - extract only on first page
if page_count == 1:
    total_match = re.search(r'Results:\*\*\s+([\d,]+)\s+of\s+([\d,]+)', result)
    total_count = int(total_match.group(2).replace(',', ''))
```

## Working Implementation Reference

See: `.claude/skills/get_glp1_trials.py:15-64` for complete, production-validated implementation.

**Stats from real usage**:
- Total trials: 1803
- Pages fetched: 2 (1000 + 803)
- Retrieval rate: 100%
- Pattern success: Validated ✅

## Testing Your Pagination

**Validation checklist**:
- ✅ First page retrieval works
- ✅ Token extraction succeeds
- ✅ Second page retrieval works
- ✅ Loop exits when no more pages
- ✅ Total count matches retrieved count
- ✅ No duplicate trials across pages

**Test with known dataset**:
```python
# Use GLP-1 (known: 1803 trials) as validation
result = get_glp1_trials()
assert result['total_count'] == 1803
assert len(result['trials_parsed']) == 1803
assert result['pages_fetched'] == 2
```
