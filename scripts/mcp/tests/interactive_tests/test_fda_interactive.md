# FDA MCP Interactive Test Script

**Purpose**: Validate FDA MCP behavior, discover quirks, and enhance Python stub based on learnings.

**MCP Server**: `fda-mcp`
**Tool Name**: `mcp__fda-mcp__fda_info`
**Python Stub**: `scripts/mcp/servers/fda_mcp/__init__.py`

---

## Test Scenarios

### Test 1: lookup_drug WITH count parameter (CRITICAL)

**Goal**: Validate that count parameter provides massive token reduction

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="semaglutide",
    search_type="general",
    count="openfda.brand_name.exact"
)
```

**Expected Behavior**:
- Response should include `meta.results.count` field
- Response size should be < 5,000 characters
- Results should contain `{term, count}` pairs
- Token usage should be ~400 tokens (vs 67,000 without count)

**Validation Criteria**:
- ✅ Response contains `results` array
- ✅ Response contains `meta` object
- ✅ `meta.results` has brand name counts
- ✅ Response size < 5,000 chars
- ✅ No nested `data.results` structure issues

**Learning Template**:
```markdown
### Learning 1: Count Parameter Token Efficiency

- **Discovery**: [What was observed]
- **Token Measurement**: [Actual response size in chars/tokens]
- **Comparison**: With count: X tokens, Without count: Y tokens (Z% reduction)
- **Critical Finding**: [Why this matters]
- **Stub Enhancement**: [What to add/change in fda_mcp/__init__.py]
```

---

### Test 2: lookup_drug WITHOUT count parameter

**Goal**: Demonstrate the problem when count parameter is omitted

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="aspirin",
    search_type="general",
    limit=5  # Use small limit to prevent timeout
)
```

**Expected Behavior**:
- Response may be very large (>10,000 chars even with limit=5)
- Without limit, could exceed 67,000 chars
- May hit 25k MCP token limit and fail

**Validation Criteria**:
- ✅ Response structure valid
- ⚠️  Response size > 10,000 chars (warning sign)
- ⚠️  Each result contains full drug label data
- ❌ Without limit, likely exceeds MCP limits

**Learning Template**:
```markdown
### Learning 2: Large Response Without Count

- **Discovery**: [Actual response size]
- **Problem**: [What breaks without count parameter]
- **Impact**: [Why this is critical for users]
- **Stub Enhancement**: [Warnings/validation to add]
```

---

### Test 3: adverse_events WITH count parameter

**Goal**: Validate adverse event counting works correctly

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="semaglutide",
    search_type="adverse_events",
    count="patient.reaction.reactionmeddrapt.exact"
)
```

**Expected Behavior**:
- Response contains adverse event terms with counts
- Format: `[{term: "Nausea", count: 1234}, ...]`
- Small response size (aggregated counts only)

**Validation Criteria**:
- ✅ Results array contains objects with `term` and `count`
- ✅ Response size < 10,000 chars
- ✅ No individual case reports (which would be huge)

**Learning Template**:
```markdown
### Learning 3: Adverse Events Count Structure

- **Discovery**: [Response structure observations]
- **Use Case**: [How this is useful]
- **Stub Enhancement**: [Documentation/examples to add]
```

---

### Test 4: drug label with field selection

**Goal**: Validate that field selection reduces response size for detailed queries

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="ozempic",
    search_type="label",
    fields_for_label="openfda.brand_name,openfda.generic_name,indications_and_usage,warnings"
)
```

**Expected Behavior**:
- Response contains only requested fields
- Smaller than retrieving all label sections
- Specific sections are properly extracted

**Validation Criteria**:
- ✅ Requested fields present in results
- ✅ Unrequested fields absent (or null)
- ✅ Response smaller than without field selection

**Learning Template**:
```markdown
### Learning 4: Field Selection Efficiency

- **Discovery**: [Field filtering observations]
- **Size Comparison**: [With fields vs without]
- **Stub Enhancement**: [Examples/guidance to add]
```

---

### Test 5: recalls search

**Goal**: Validate recalls dataset structure and identify if count parameter needed

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="insulin",
    search_type="recalls",
    limit=10
)
```

**Expected Behavior**:
- Recalls dataset is relatively small
- Count parameter may be optional for recalls
- Standard recall fields present

**Validation Criteria**:
- ✅ Results contain recall-specific fields (status, reason_for_recall, classification)
- ✅ Response size manageable without count
- ✅ Recall data structure documented

**Learning Template**:
```markdown
### Learning 5: Recalls Dataset Characteristics

- **Discovery**: [Dataset size, structure]
- **Count Parameter**: [Needed or optional?]
- **Stub Enhancement**: [Quirks/guidance to add]
```

---

### Test 6: shortages search

**Goal**: Validate shortages dataset structure

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="amoxicillin",
    search_type="shortages",
    limit=5
)
```

**Expected Behavior**:
- Shortages dataset is small
- Count parameter optional
- Shortage-specific fields present

**Validation Criteria**:
- ✅ Results contain shortage fields (status, product_description, reason)
- ✅ Response size manageable
- ✅ Data structure documented

**Learning Template**:
```markdown
### Learning 6: Shortages Dataset Characteristics

- **Discovery**: [Dataset observations]
- **Count Parameter**: [Needed or optional?]
- **Stub Enhancement**: [Documentation to add]
```

---

### Test 7: Error handling - missing required parameter

**Goal**: Validate error messages when required parameters missing

**Test Code**:
```python
from fda_mcp import lookup_drug

try:
    result = lookup_drug(
        search_type="general"
        # Missing search_term - should fail
    )
except Exception as e:
    print(f"Error: {e}")
```

**Expected Behavior**:
- Clear error message about missing search_term
- No cryptic MCP errors
- Helpful guidance on what's required

**Validation Criteria**:
- ✅ Error raised (not silent failure)
- ✅ Error message mentions required parameter
- ✅ Error is user-friendly

**Learning Template**:
```markdown
### Learning 7: Error Handling

- **Discovery**: [Error message quality]
- **User Experience**: [Is error clear?]
- **Stub Enhancement**: [Validation to add]
```

---

### Test 8: OR operator failure (documented quirk)

**Goal**: Confirm that OR operators don't work as expected

**Test Code**:
```python
from fda_mcp import lookup_drug

result = lookup_drug(
    search_term="semaglutide OR liraglutide",  # OR should NOT work
    search_type="general",
    count="openfda.brand_name.exact"
)
```

**Expected Behavior**:
- Query may return 404 or unexpected results
- OR operator doesn't work as in traditional search engines

**Validation Criteria**:
- ⚠️  Results don't match expected OR behavior
- ⚠️  May return 404 error
- ✅ Confirms documented quirk

**Learning Template**:
```markdown
### Learning 8: OR Operator Behavior

- **Discovery**: [What actually happened]
- **Workaround**: [Parallel queries instead]
- **Stub Enhancement**: [Warning/example to add]
```

---

## Test Execution Instructions

1. **Run each test** in sequence
2. **Measure response sizes** (token count if available, character count otherwise)
3. **Validate against criteria** (✅ = pass, ⚠️  = warning, ❌ = fail)
4. **Document learnings** using templates above
5. **Identify stub enhancements**
6. **Update fda_mcp/__init__.py** with improvements
7. **Save results** to `test_results/fda_test_results.md`

---

## Post-Test Analysis

After running all tests, answer:

1. **What are the 3 most critical learnings?**
2. **Which stub enhancements are highest priority?**
3. **Are there undocumented quirks discovered?**
4. **Do examples in the stub need updates?**
5. **Is the count parameter guidance sufficient?**

---

## Stub Enhancement Checklist

After testing, check fda_mcp/__init__.py for:

- [ ] Count parameter importance emphasized in all relevant places
- [ ] Token reduction statistics included (67k→400 tokens)
- [ ] OR operator warning clearly stated
- [ ] Field selection examples comprehensive
- [ ] Error handling guidance complete
- [ ] All search_type options documented with examples
- [ ] Response structure quirks documented
- [ ] Undocumented learnings from testing added

---

## Success Criteria

✅ All 8 tests executed
✅ All learnings documented
✅ Token measurements recorded
✅ Stub enhanced based on findings
✅ Enhanced stub validated (no regressions)
