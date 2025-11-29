# CRITICAL BUG: products-by-approval-pathway Returns Wrong Drugs

**Status**: 🔴 CRITICAL - Skill returns incorrect results for therapeutic area filtering
**Date Discovered**: 2025-11-29
**Severity**: High - Affects all pathway queries with therapeutic area filters
**Impact**: Users get completely wrong drug lists (arthritis drugs instead of Alzheimer's drugs)

---

## Problem Summary

The `products-by-approval-pathway` skill v4.0 returns **completely incorrect drugs** when filtering by therapeutic area + pathway.

**Example Query**:
```
What Alzheimer's disease drugs received priority review designation from the FDA?
```

**Expected Result**:
- ARICEPT (donepezil)
- NAMENDA (memantine)
- LEQEMBI (lecanemab)
- ADUHELM (aducanumab)
- etc.

**Actual Result** (WRONG):
1. HUMIRA (adalimumab) - **Arthritis drug**
2. PREDNISONE - **Steroid**
3. REMICADE (infliximab) - **Autoimmune drug**
4. NEXIUM (esomeprazole) - **Acid reflux drug**
5. ASPIRIN - **Pain reliever**
6. BAYER - **Aspirin brand**
7. OMEPRAZOLE - **Acid reflux drug**
8. ASPICA (ASPIRIN) - **Pain reliever**

**None of these drugs are approved for Alzheimer's disease!**

---

## Root Cause

### Current Implementation (v4.0 Hybrid Adverse Events Discovery)

```python
# STEP 1: Query adverse events database
query = f"patient.drug.drugindication:{therapeutic_area}"

# Example for Alzheimer's:
# patient.drug.drugindication:Alzheimer
```

**What this actually finds**:
- Adverse event reports where the **patient has Alzheimer's disease** as a medical condition
- Includes ALL drugs those patients took (for ANY condition)
- ✅ Drugs approved FOR Alzheimer's (ARICEPT, NAMENDA)
- ❌ Drugs for comorbid conditions (HUMIRA for arthritis, NEXIUM for GERD, etc.)

**The critical flaw**:
`patient.drug.drugindication` = **Patient's medical diagnoses**, NOT **Drug's approved indication**

### Why This Happens

Alzheimer's patients often have multiple conditions:
- Arthritis (HUMIRA, PREDNISONE)
- GERD/acid reflux (NEXIUM, OMEPRAZOLE)
- Cardiovascular disease (ASPIRIN)
- Autoimmune conditions (REMICADE)

The adverse events database captures **all drugs taken by Alzheimer's patients**, not just Alzheimer's treatments.

---

## Evidence from Execution Log

```bash
$ python3 .claude/skills/products-by-approval-pathway/scripts/get_products_by_approval_pathway.py \
    "priority_review" "Alzheimer's disease"

# Output:
✓ Found 8 drugs with priority review designation

Drugs with Priority Review (8 found):
1. HUMIRA (172,744 adverse event reports)          # ❌ Arthritis drug
2. PREDNISONE (88,628 adverse event reports)       # ❌ Steroid
3. REMICADE (76,032 adverse event reports)         # ❌ Autoimmune drug
4. NEXIUM (74,923 adverse event reports)           # ❌ Acid reflux drug
5. ASPIRIN (70,945 adverse event reports)          # ❌ Pain reliever
6. BAYER (70,909 adverse event reports)            # ❌ Aspirin brand
7. OMEPRAZOLE (70,893 adverse event reports)       # ❌ Acid reflux drug
8. ASPICA (ASPIRIN) (70,874 adverse event reports) # ❌ Pain reliever
```

**Reality Check**: HUMIRA is indicated for rheumatoid arthritis, Crohn's disease, and psoriasis. It has ZERO Alzheimer's indication.

---

## Impact Assessment

### Queries Affected
- ✅ **Works correctly**: "All orphan drugs" (no therapeutic area filter)
- ✅ **Works correctly**: "All priority review drugs" (no therapeutic area filter)
- ❌ **BROKEN**: "Alzheimer's drugs with priority review" (therapeutic area + pathway)
- ❌ **BROKEN**: "Diabetes drugs with orphan designation" (therapeutic area + pathway)
- ❌ **BROKEN**: Any pathway query WITH therapeutic area filtering

### User Trust Impact
- Users asking for Alzheimer's drugs get arthritis drugs
- Results look plausible (FDA-approved drugs with correct pathway)
- **Silent failure**: No error message, just wrong data
- High adverse event counts make wrong drugs look "important"

### Scope
- Affects **all 89 skills** that might use this as a reference pattern
- Semantic matcher now routes pathway queries to this broken skill (score: 23)
- Marked as `is_generic: true`, so it will be reused for all pathway queries

---

## Correct Implementation Approaches

### Option 1: Drug Label Search (Recommended)

Query FDA drug labels for drugs approved for the indication:

```python
# STEP 1: Find drugs with Alzheimer's indication in drug labels
lookup_drug(
    search_term="indications_and_usage:Alzheimer",
    search_type="label",
    count="openfda.brand_name.exact",
    limit=100
)

# STEP 2: For each drug, check pathway designation
lookup_drug(
    search_term=f"openfda.brand_name.exact:{brand_name}",
    search_type="label",
    fields_for_label="submissions"
)
# Check: submissions.submission_property_type.code == "Orphan" / "PRIORITY"
```

**Pros**:
- ✅ Returns drugs actually approved FOR the indication
- ✅ Uses official FDA drug label data
- ✅ Accurate therapeutic area filtering

**Cons**:
- ⚠️ More complex query pattern
- ⚠️ May miss some drugs if label text varies

### Option 2: Reverse Query (All Pathway Drugs → Filter by Indication)

```python
# STEP 1: Get all drugs with priority review designation
lookup_drug(
    search_term="submissions.submission_property_type.code:PRIORITY",
    search_type="label",
    count="openfda.brand_name.exact",
    limit=100
)

# STEP 2: For each drug, check if indicated for Alzheimer's
lookup_drug(
    search_term=f"openfda.brand_name.exact:{brand_name} AND indications_and_usage:Alzheimer",
    search_type="label"
)
```

**Pros**:
- ✅ Guaranteed to find all pathway drugs
- ✅ Simple pathway filtering

**Cons**:
- ⚠️ Two-pass query (slower)
- ⚠️ Limited to 100 pathway drugs

### Option 3: Remove Therapeutic Area Support

Mark the skill as NOT supporting therapeutic area filtering:

```python
def get_products_by_approval_pathway(pathway: str, therapeutic_area: Optional[str] = None):
    if therapeutic_area:
        raise ValueError(
            "Therapeutic area filtering not supported. "
            "Use this skill to find ALL drugs with the pathway, "
            "then manually filter by indication."
        )
```

**Pros**:
- ✅ Simple fix
- ✅ Prevents wrong results
- ✅ Forces user to use correct tool

**Cons**:
- ❌ Loses functionality
- ❌ User frustration

---

## Recommended Fix

**Approach**: Option 1 (Drug Label Search)

**Implementation**:
1. Create new skill: `get_drugs_by_indication_and_pathway`
2. Use drug label search with indication filtering
3. Cross-reference with submission metadata for pathway
4. Mark `products-by-approval-pathway` as deprecated or limit to pathway-only queries
5. Update semantic matcher to prefer the new skill for indication+pathway queries

**New Function Signature**:
```python
def get_drugs_by_indication_and_pathway(
    indication: str,
    pathway: str,  # priority_review | orphan | standard_review
    search_type: str = "exact"  # exact | contains
) -> dict:
    """
    Find FDA-approved drugs by indication AND regulatory pathway.

    Uses drug label search for accurate indication filtering.

    Args:
        indication: Drug indication (e.g., "Alzheimer", "diabetes")
        pathway: Regulatory pathway designation
        search_type: How to match indication (exact or contains)

    Returns:
        dict with drugs, count, and detailed metadata
    """
```

---

## Testing Plan

### Test Cases

```python
# Test 1: Alzheimer's + Priority Review
result = get_drugs_by_indication_and_pathway("Alzheimer", "priority_review")
# Expected: ARICEPT, NAMENDA, LEQEMBI, ADUHELM
# NOT: HUMIRA, NEXIUM, ASPIRIN

# Test 2: Diabetes + Orphan Designation
result = get_drugs_by_indication_and_pathway("diabetes", "orphan")
# Expected: Drugs specifically approved for diabetes with orphan designation
# NOT: All drugs taken by diabetic patients

# Test 3: Cancer + Priority Review
result = get_drugs_by_indication_and_pathway("cancer", "priority_review")
# Expected: Cancer drugs with priority review
# Verify against known cancer drugs (KEYTRUDA, OPDIVO, etc.)
```

### Validation Criteria

For each result:
1. ✅ Drug's FDA label mentions the queried indication
2. ✅ Drug's submission metadata shows the queried pathway
3. ❌ No drugs for unrelated conditions
4. ❌ No generic drugs taken by patients with the condition

---

## Immediate Actions Required

1. **Mark skill as broken** in index.json:
   ```json
   {
     "name": "get_products_by_approval_pathway",
     "health_status": "broken",
     "health_issues": [
       "Therapeutic area filtering returns wrong drugs (comorbid conditions)",
       "Uses patient diagnosis instead of drug indication"
     ]
   }
   ```

2. **Remove `is_generic: true` flag** to prevent automatic reuse

3. **Update trigger keywords** to remove therapeutic area combinations:
   ```json
   "trigger_keywords": [
     "all priority review drugs",
     "all orphan drugs",
     "all standard review"
     // Remove: "alzheimer priority review", etc.
   ]
   ```

4. **Create warning in SKILL.md**:
   ```markdown
   ## ⚠️ CRITICAL LIMITATION

   **DO NOT use this skill with therapeutic area filtering!**

   The adverse events method finds drugs taken by patients WITH the condition,
   not drugs approved FOR the condition.

   ❌ WRONG: get_products_by_approval_pathway("priority_review", "Alzheimer")
   → Returns arthritis drugs, acid reflux drugs, etc.

   ✅ CORRECT: Use for pathway-only queries
   → get_products_by_approval_pathway("priority_review", None)
   ```

5. **Invoke pharma-search-specialist** to create correct skill for Alzheimer's priority review query

---

## Long-Term Solution

**Goal**: Create robust indication + pathway filtering skill

**Requirements**:
- Accurate drug indication matching (from FDA labels)
- Pathway designation cross-reference (from submission metadata)
- Support for exact and fuzzy indication matching
- Proper error handling when no drugs found
- Clear documentation of method limitations

**Timeline**:
- Immediate: Mark current skill as broken, add warnings
- Short-term (next session): Create correct implementation
- Long-term: Deprecate v4.0 hybrid method for therapeutic area queries

---

## Related Issues

- Semantic matcher fix (completed 2025-11-29) - needs to be aware of skill health status
- Strategy system should check health status before REUSE
- Index needs health status tracking and automatic warnings

---

## References

- FDA Adverse Events API: https://open.fda.gov/apis/drug/event/
- FDA Drug Labels API: https://open.fda.gov/apis/drug/label/
- Skill location: `.claude/skills/products-by-approval-pathway/`
- Discovery log: User session 2025-11-29 ~00:48 AM

---

## Notes

This bug demonstrates why **data source validation is critical**. The v4.0 "breakthrough" method looked promising (100% coverage!) but had a fundamental flaw in understanding what the data actually represents.

**Key lesson**: Patient medical history ≠ Drug's approved indication

The adverse events database is excellent for finding prescribed drugs, but terrible for finding drugs approved for specific indications.
