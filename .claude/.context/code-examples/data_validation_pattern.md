# Data Validation Pattern for Skills

## Purpose
Ensure skills collect valid, non-empty data before returning results. Prevents strategic agents from analyzing insufficient or invalid data.

## Pattern

### Basic Validation Structure

```python
def get_therapeutic_area_data():
    """Collect data with validation."""

    # 1. Execute data collection
    result = mcp_server_call(...)

    # 2. Validate result structure
    if not result:
        raise ValueError("No data returned from MCP server")

    # 3. Validate data content
    if isinstance(result, dict):
        # For JSON responses (FDA, PubMed, etc.)
        if 'error' in result:
            raise ValueError(f"API error: {result['error']}")
        if 'results' in result and len(result['results']) == 0:
            raise ValueError("No results found - check search terms")

    elif isinstance(result, str):
        # For markdown responses (CT.gov)
        if 'No results found' in result or len(result) < 100:
            raise ValueError("No trials found - check search terms")

    # 4. Extract and validate key metrics
    count = extract_count(result)
    if count == 0:
        raise ValueError("Data collection returned 0 records")

    # 5. Return validated data
    return {
        'count': count,
        'data': result,
        'validated': True
    }
```

## Common Validation Patterns

### CT.gov Trials Validation

```python
def get_trials():
    result = search(term="...", pageSize=100)

    # Validate markdown response
    if not isinstance(result, str):
        raise TypeError("Expected markdown string from CT.gov")

    # Extract count
    count_match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', result)
    if not count_match:
        raise ValueError("Could not parse trial count from response")

    total_count = int(count_match.group(1))
    if total_count == 0:
        raise ValueError(f"No trials found for search term")

    return {'total_count': total_count, 'trials_summary': result}
```

### FDA Drugs Validation

```python
def get_fda_drugs():
    results = lookup_drug(search_term="...", search_type="general")

    # Validate JSON response
    if not isinstance(results, dict):
        raise TypeError("Expected dict from FDA API")

    if 'error' in results:
        raise ValueError(f"FDA API error: {results['error']}")

    # Extract drug list
    drugs = {}
    if 'data' in results and 'results' in results['data']:
        for item in results['data']['results']:
            # ... extraction logic ...
            pass

    if len(drugs) == 0:
        raise ValueError("No FDA drugs found - check search terms or known drug list")

    return drugs
```

### Multi-Source Validation

```python
def get_multi_source_data():
    """Collect from multiple sources with validation."""

    errors = []
    results = {}

    # Try CT.gov
    try:
        results['trials'] = get_trials()
    except Exception as e:
        errors.append(f"CT.gov: {str(e)}")

    # Try FDA
    try:
        results['fda'] = get_fda_drugs()
    except Exception as e:
        errors.append(f"FDA: {str(e)}")

    # Require at least one source to succeed
    if len(results) == 0:
        raise ValueError(f"All data sources failed: {'; '.join(errors)}")

    # Warn about partial failures
    if errors:
        print(f"WARNING: Some sources failed: {'; '.join(errors)}", file=sys.stderr)

    return results
```

## Validation Checklist

Before returning data, validate:

- [ ] Response is not None/empty
- [ ] Response structure matches expected format (dict vs string)
- [ ] No error fields in response
- [ ] Count/total > 0 (if applicable)
- [ ] Key fields are present (brand_name, title, etc.)
- [ ] Data can be parsed/extracted successfully

## Error Messages

Use descriptive error messages that help debug:

❌ Bad: `raise ValueError("Invalid data")`
✅ Good: `raise ValueError("No trials found for 'KRAS inhibitor' - check search term spelling")`

❌ Bad: `raise Exception("Error")`
✅ Good: `raise ValueError("FDA API returned 0 drugs - expected LUMAKRAS/KRAZATI in results")`

## When to Validate

**Always validate**:
- Data collection from external APIs
- Response structure (type checking)
- Count > 0 for search results
- Required fields present

**Optional validation**:
- Data quality (duplicate checking)
- Completeness (all expected fields populated)
- Consistency (cross-source validation)

## Integration with __main__ Block

```python
if __name__ == "__main__":
    try:
        result = get_data()
        print(f"✓ Data collection successful: {result['count']} records")
        print(result['summary'])
    except ValueError as e:
        print(f"✗ Data validation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)
```

This allows skills to be tested standalone and will exit with error code if validation fails.
