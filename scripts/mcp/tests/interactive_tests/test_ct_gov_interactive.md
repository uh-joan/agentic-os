# CT.gov MCP Interactive Test Script

**Purpose**: Validate ClinicalTrials.gov MCP behavior, discover quirks, and enhance Python stub.

**MCP Server**: `ct-gov-mcp`
**Tool Name**: `mcp__ct-gov-mcp__ct_gov_studies`
**Python Stub**: `scripts/mcp/servers/ct_gov_mcp/__init__.py`

---

## Test Scenarios

### Test 1: Basic search with condition

**Goal**: Validate basic search works and response format

**Test Code**:
```python
from ct_gov_mcp import search

result = search(
    condition="diabetes",
    pageSize=5
)
```

**Expected Behavior**:
- Returns markdown text (not JSON)
- Contains trial summaries with NCT IDs
- Shows count of total results

**Validation**:
- ✅ Response is string (markdown format)
- ✅ Contains NCT IDs
- ✅ Shows result count
- ✅ Response size manageable

---

### Test 2: Phase filter validation

**Goal**: Test that PHASE2 format works (not "Phase 2")

**Test Code**:
```python
result = search(
    condition="obesity",
    phase="PHASE3",
    pageSize=10
)
```

**Expected Behavior**:
- Returns Phase 3 trials only
- Phase format PHASE3 works correctly

**Validation**:
- ✅ Results filtered to Phase 3
- ✅ Uppercase format works
- ✅ Response contains phase information

---

### Test 3: Status filter

**Goal**: Validate status filter with uppercase underscore format

**Test Code**:
```python
result = search(
    intervention="semaglutide",
    status="RECRUITING",
    pageSize=10
)
```

**Expected Behavior**:
- Returns only recruiting trials
- Status filter works correctly

**Validation**:
- ✅ Results show recruiting status
- ✅ Uppercase format works
- ✅ Filter applied correctly

---

### Test 4: Pagination test

**Goal**: Test pageSize limits and pagination

**Test Code**:
```python
# Test 1: Small page
small = search(
    condition="cancer",
    pageSize=5
)

# Test 2: Large page
large = search(
    condition="cancer",
    pageSize=100
)
```

**Expected Behavior**:
- pageSize limits results correctly
- Max pageSize is 1000 (different from FDA)

**Validation**:
- ✅ Small pageSize returns 5 results
- ✅ Large pageSize returns 100 results
- ✅ No errors with different page sizes

---

### Test 5: Multiple filters combined

**Goal**: Test combining multiple search parameters

**Test Code**:
```python
result = search(
    condition="diabetes",
    intervention="insulin",
    phase="PHASE3",
    status="COMPLETED",
    pageSize=20
)
```

**Expected Behavior**:
- All filters applied
- Results match all criteria
- Response manageable size

**Validation**:
- ✅ Results filtered correctly
- ✅ All criteria applied
- ✅ Response coherent

---

### Test 6: Get study details by NCT ID

**Goal**: Validate retrieving specific study

**Test Code**:
```python
from ct_gov_mcp import get_study

result = get_study(
    nct_id="NCT04000165"
)
```

**Expected Behavior**:
- Returns detailed study information
- Markdown format with full details

**Validation**:
- ✅ Study details returned
- ✅ Markdown format
- ✅ Complete information

---

### Test 7: Suggest (autocomplete) functionality

**Goal**: Test term suggestion feature

**Test Code**:
```python
from ct_gov_mcp import suggest

result = suggest(
    input="diabet",
    dictionary="Condition"
)
```

**Expected Behavior**:
- Returns condition suggestions
- Helps with spelling/autocomplete

**Validation**:
- ✅ Suggestions returned
- ✅ Relevant to input
- ✅ Useful for query building

---

## Critical Areas to Test

1. **Markdown parsing** - How to extract structured data from text
2. **Phase format** - Confirm PHASE2 vs "Phase 2"
3. **Status format** - Confirm RECRUITING vs "Recruiting"
4. **PageSize limits** - Max 1000 vs FDA's 100
5. **Response size** - Token usage for different page sizes
6. **NCT ID format** - Validate NCT + 8 digits

---

## Learning Focus

- Response format challenges (markdown vs JSON)
- Parameter format requirements (uppercase, underscores)
- Pagination differences from other MCPs
- Token usage patterns
- Practical parsing examples needed

---

## Success Criteria

✅ All 7 tests executed
✅ Markdown response format documented
✅ Phase/status format validated
✅ PageSize limits confirmed
✅ Stub enhanced with findings
