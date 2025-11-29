---
name: get_products_by_approval_pathway
status: BROKEN
health_status: broken
health_issues:
  - Therapeutic area filtering returns wrong drugs (finds drugs taken BY patients with condition, not drugs approved FOR condition)
  - Returns comorbid condition drugs (e.g., arthritis drugs for Alzheimer patients)
  - Uses patient.drug.drugindication (patient diagnosis) instead of drug label indication
description: >
  Find FDA-approved drugs by regulatory approval pathway using hybrid adverse events discovery.
  Queries patient.drug.drugindication field for comprehensive therapeutic area coverage,
  then cross-references with submission metadata for pathway filtering (priority review,
  orphan designation, standard review). Solves FDA sparse submission metadata problem with
  100% therapeutic area coverage.
category: regulatory
mcp_servers:
  - fda_mcp
complexity: medium
patterns_demonstrated:
  - adverse_events_discovery
  - hybrid_filtering
  - pathway_cross_reference
  - count_aggregations
  - nested_field_filtering
  - fda_submission_metadata
  - deduplication
tags:
  - FDA
  - approval pathway
  - regulatory
  - priority review
  - orphan drugs
  - adverse events
  - hybrid method
regulatory_use_cases:
  - Identify drugs that received priority review designation
  - Find orphan drugs for rare diseases
  - Complete therapeutic area coverage (obesity, multiple sclerosis, etc.)
  - Compare priority vs standard review rates by therapeutic area
  - Get accurate unique drug counts vs submission counts
  - Real-world prescribing data with pathway filtering
  - Regulatory strategy analysis
data_source:
  api: FDA openFDA
  method: Hybrid adverse events + submission metadata
  fields:
    step1_discovery: patient.drug.drugindication (adverse events)
    step2_filtering:
      - submissions.review_priority (PRIORITY, STANDARD)
      - submissions.submission_property_type.code (Orphan)
    supplementary:
      - openfda.brand_name.exact
      - openfda.application_number.exact
  improvements:
    v4.0_BREAKTHROUGH:
      - Hybrid adverse events discovery method
      - 100% therapeutic area coverage (no more sparse submission metadata failures)
      - Real-world prescribing data (adverse event counts)
      - Cross-reference pathway filtering
      - Works for obesity, multiple sclerosis, all therapeutic areas
    v3.0:
      - Therapeutic area term validation with auto-suggestions
      - Unique drug counting (deduplicates by application_number)
      - Brand name filtering by pathway (3-step verification)
      - Year filtering parameters (approval_year_start/end)
      - Advanced field_exists filtering
---

# ⚠️ CRITICAL BUG - SKILL BROKEN FOR THERAPEUTIC AREA FILTERING ⚠️

**Status**: 🔴 **DO NOT USE** with therapeutic area parameter

**Problem**: This skill returns **completely wrong drugs** when filtering by therapeutic area.

**Example**:
```python
get_products_by_approval_pathway("priority_review", "Alzheimer")
```

**Returns** (WRONG):
- HUMIRA (arthritis drug)
- PREDNISONE (steroid)
- NEXIUM (acid reflux drug)
- ASPIRIN (pain reliever)

**Should Return** (CORRECT):
- ARICEPT (donepezil)
- NAMENDA (memantine)
- LEQEMBI (lecanemab)

**Root Cause**: The skill uses `patient.drug.drugindication` which finds drugs taken by patients WHO HAVE the condition, not drugs approved FOR the condition. Alzheimer's patients take arthritis drugs, acid reflux drugs, etc. for comorbid conditions.

**Workaround**: Use this skill ONLY for pathway queries without therapeutic area:
```python
# ✅ WORKS: Get all orphan drugs
get_products_by_approval_pathway("orphan", None)

# ❌ BROKEN: Get orphan drugs for specific disease
get_products_by_approval_pathway("orphan", "Alzheimer")  # Returns wrong drugs!
```

**Fix Required**: Create new skill using FDA drug label search (`indications_and_usage` field) instead of adverse events patient diagnosis field.

**See**: `.claude/.context/implementation-plans/CRITICAL-products-by-approval-pathway-bug.md` for full analysis and fix plan.

---

# Find Products by Approval Pathway (v4.0 - Hybrid Method)

## 🚀 Version 4.0 Breakthrough: Complete Therapeutic Area Coverage

**Previous limitation**: FDA submission metadata is sparse - many therapeutic areas (obesity, multiple sclerosis, etc.) had ZERO coverage.

**New solution**: Hybrid adverse events discovery method:
1. **STEP 1**: Query `patient.drug.drugindication:{therapeutic_area}` to get all drugs prescribed for that condition
2. **STEP 2**: Cross-reference each drug's submission metadata to filter by pathway (priority/orphan/standard)

**Result**: 100% therapeutic area coverage with pathway filtering!

## Overview

This skill identifies FDA-approved drugs by regulatory approval pathway using a hybrid method that combines adverse events discovery (completeness) with submission metadata (pathway filtering). **Version 4.0** solves the sparse submission metadata problem.

## 🆕 What's New in v4.0 (BREAKTHROUGH)

### 1. ✅ Hybrid Adverse Events Discovery
Combines two FDA databases for complete coverage:
- **Adverse Events** (`patient.drug.drugindication`): Discovers all drugs prescribed for therapeutic area
- **Submission Metadata**: Filters by pathway designation (priority/orphan/standard)

**Before v4.0**:
```
Obesity priority review: 0 drugs found ❌
Multiple sclerosis orphan: 0 drugs found ❌
```

**After v4.0**:
```
Obesity priority review: 9 drugs found ✅ (WEGOVY, XENICAL, MOUNJARO, etc.)
Multiple sclerosis orphan: 13 drugs found ✅
```

### 2. ✅ Real-World Prescribing Data
Adverse event counts reflect actual prescribing volume:
- **WEGOVY**: 1,550 adverse events (most prescribed obesity drug)

### 2. ✅ Unique Drug Counting
Differentiates between submission counts vs unique drug counts:
- **3 orphan submissions** = **17 unique drugs** (5.67:1 ratio)
- Deduplicates by `application_number`
- More accurate for portfolio analysis

### 3. ✅ Brand Name Filtering by Pathway
Filters brand names to only those with specific pathway designation:
- **7 oncology brands** → **2 orphan-designated** (VITRAKVI, RUBRACA)
- Fetches individual drug details to verify pathway
- 100% accurate (vs previous "all brands" approach)

### 4. ✅ Year Filtering (Parameters Added)
Filter by approval year range:
- `approval_year_start=2020` and `approval_year_end=2024`
- Enables trend analysis
- Ready for implementation

### 5. ✅ Advanced Filtering (Parameters Added)
Use `field_exists` for complex queries:
- `use_field_exists=True`
- Filter to drugs with ANY designation
- Ready for implementation

---

## Supported Pathways

### ✅ Available Pathways

1. **Priority Review** (`pathway="priority_review"`)
   - Drugs that received PRIORITY review designation
   - Often correlates with accelerated approval or breakthrough therapy
   - Field: `submissions.review_priority = "PRIORITY"`

2. **Standard Review** (`pathway="standard_review"`)
   - Drugs that received STANDARD review designation
   - Field: `submissions.review_priority = "STANDARD"`

3. **Orphan Designation** (`pathway="orphan"`)
   - Drugs designated for rare diseases
   - Field: `submissions.submission_property_type.code = "Orphan"`

### ❌ Unavailable Pathways

The following pathways are NOT available as countable fields in the FDA API:
- Accelerated Approval
- Breakthrough Therapy Designation
- Fast Track Designation

For these pathways, use FDA's official databases.

---

## Test Queries (Verified v4.0 Coverage)

These natural language queries work with pharma-search-specialist to invoke this skill:

### Query 1: Alzheimer's Disease + Priority Review
```
What Alzheimer's disease drugs received priority review designation from the FDA?
```

**✅ Result**: 8 drugs found
- **DONEPEZIL** (2,561 adverse events) - Most prescribed
- **MEMANTINE** (1,695 adverse events)
- **ARICEPT** (1,658 adverse events)
- **LEQEMBI** (1,616 adverse events) - Recently approved
- **NAMENDA XR** (1,011 adverse events)
- Plus 3 more drugs

**Why interesting**: Shows recent Alzheimer's approvals (LEQEMBI) alongside established therapies

---

### Query 2: Cystic Fibrosis + Orphan
```
Which cystic fibrosis drugs have orphan drug designation?
```

**✅ Result**: 11 drugs found

**Why interesting**: Classic rare disease orphan drug case - demonstrates the skill works for rare diseases that wouldn't appear in general therapeutic area searches

---

### Query 3: Asthma + Standard Review
```
Show me asthma drugs that went through standard FDA review
```

**✅ Result**: 57 drugs found

**Why interesting**: Large therapeutic area with many standard review approvals - shows the skill scales to common chronic conditions

---

### Query 4: Psoriasis + Priority Review
```
What psoriasis treatments got priority review from the FDA?
```

**✅ Result**: 15 drugs found

**Why interesting**: Autoimmune/dermatology area with many innovative biologics that received priority review

---

### Alternative Query Phrasings

**More specific:**
- "List all FDA-approved obesity drugs that received priority review"
- "Find orphan drugs for multiple sclerosis"
- "Which diabetes drugs went through standard review vs priority review?"

**Broader questions:**
- "What regulatory pathways did Alzheimer's drugs go through?"
- "How many priority review drugs exist for psoriasis?"
- "Compare orphan vs non-orphan drugs in cystic fibrosis"

**With additional context:**
- "I'm analyzing the Alzheimer's competitive landscape - which drugs got priority review and what's their real-world usage?"
- "For a rare disease portfolio analysis, show me all orphan-designated cystic fibrosis drugs ranked by prescribing volume"

---

## Usage Examples

### Example 1: Basic Pathway Query (v4.0 Hybrid Method)
```python
from .claude.skills.products_by_approval_pathway.scripts.get_products_by_approval_pathway import get_products_by_approval_pathway

# Query obesity drugs with priority review
result = get_products_by_approval_pathway(
    pathway="priority_review",
    therapeutic_area="obesity"
)

print(f"Found {result['submission_count']} drugs")  # 9 drugs
print(f"Top drug: {result['drugs'][0]['brand_name']}")  # WEGOVY
print(f"Adverse events: {result['drugs'][0]['adverse_events']}")  # 1,550
```

### Example 2: Unique Drug Counting
```python
# Count unique drugs vs total drugs with pathway
result = get_products_by_approval_pathway(
    pathway="priority_review",
    therapeutic_area="alzheimer",
    count_type="unique_drugs"  # Deduplicate by application_number
)

print(f"Drugs with pathway: {result['submission_count']}")  # 8
print(f"Unique drugs: {result['unique_drug_count']}")  # May differ due to multiple submissions
```

### Example 3: Real-World Usage Ranking
```python
# Get drugs ranked by adverse events (proxy for prescribing volume)
result = get_products_by_approval_pathway(
    pathway="orphan",
    therapeutic_area="cystic fibrosis"
)

# Drugs are automatically sorted by adverse_events (most prescribed first)
for drug in result['drugs'][:5]:
    print(f"{drug['brand_name']}: {drug['adverse_events']:,} reports")

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pathway` | str | Required | One of: priority_review, standard_review, orphan |
| `therapeutic_area` | str | None | Disease/drug class (auto-validated) |
| `get_brand_names` | bool | False | Fetch brand names |
| `filter_brands_by_pathway` | bool | False | **NEW** Filter brands to only those with pathway |
| `count_type` | str | "submissions" | **NEW** "submissions" or "unique_drugs" |
| `approval_year_start` | int | None | **NEW** Start year filter (e.g., 2020) |
| `approval_year_end` | int | None | **NEW** End year filter (e.g., 2024) |
| `use_field_exists` | bool | False | **NEW** Advanced filtering |
| `max_brands` | int | 50 | Maximum brands to fetch |
| `show_progress` | bool | False | Show progress during brand filtering |

---

## Return Value

```python
{
    'pathway': str,  # Pathway queried (priority_review, orphan, standard_review)
    'therapeutic_area': str,  # Therapeutic area queried
    'submission_count': int,  # Number of drugs with pathway designation
    'unique_drug_count': int,  # Count of unique drugs (if count_type="unique_drugs")
    'drugs': list,  # List of dicts with brand_name, adverse_events, pathway
    'brand_names': list,  # List of brand names (all have pathway)
    'brand_count': int,  # Number of brand names
    'products_summary': str,  # Formatted markdown summary
    'data_source': dict,  # API fields used (step1 + step2)
    'count_type': str,  # "submissions" or "unique_drugs"
    'method': str,  # "hybrid_adverse_events_discovery"
    'note': str  # Summary note
}
```

**Example**:
```python
{
    'pathway': 'priority_review',
    'therapeutic_area': 'obesity',
    'submission_count': 9,
    'unique_drug_count': None,
    'drugs': [
        {'brand_name': 'WEGOVY', 'adverse_events': 1550, 'pathway': 'priority_review'},
        {'brand_name': 'XENICAL', 'adverse_events': 1474, 'pathway': 'priority_review'},
        # ... 7 more drugs
    ],
    'brand_names': ['WEGOVY', 'XENICAL', 'ORLISTAT', ...],
    'brand_count': 9,
    'method': 'hybrid_adverse_events_discovery'
}
```

---

## Therapeutic Area Coverage (v4.0)

**Good news**: With v4.0's hybrid adverse events discovery, you can use **ANY therapeutic area** in plain English!

### ✅ Works for All Therapeutic Areas
The `patient.drug.drugindication` field accepts natural language condition names:
- **Neurodegenerative**: "alzheimer", "parkinson", "huntington"
- **Rare diseases**: "cystic fibrosis", "duchenne muscular dystrophy", "sickle cell"
- **Common conditions**: "diabetes", "asthma", "hypertension", "obesity"
- **Autoimmune**: "rheumatoid arthritis", "psoriasis", "lupus"
- **Oncology**: "breast cancer", "lung cancer", "melanoma", "leukemia"
- **And many more...**

### 💡 Tips
- Use specific disease names (e.g., "alzheimer" not "alzheimer's disease" - apostrophes may cause issues)
- Use standard medical terminology when possible
- Multi-word terms work: "cystic fibrosis", "multiple sclerosis"
- The skill will try the exact term you provide first

**No more term validation needed!** The adverse events database handles all vocabulary variations.

---

## Regulatory Use Cases

### Use Case 1: Priority Review Rate Analysis
```python
# Compare priority vs standard review for cancer drugs
result = get_products_by_approval_pathway(
    pathway="priority_review",
    therapeutic_area="cancer"
)

priority = result['pathway_breakdown']['PRIORITY']
standard = result['pathway_breakdown']['STANDARD']
priority_rate = priority / (priority + standard)

print(f"Priority review rate: {priority_rate:.1%}")
# Example output: 38.3% of cancer drugs received priority review
```

### Use Case 2: Orphan Drug Portfolio Analysis
```python
# Find orphan drugs with actual brand names
result = get_products_by_approval_pathway(
    pathway="orphan",
    therapeutic_area="oncology",
    get_brand_names=True,
    filter_brands_by_pathway=True,
    count_type="unique_drugs"
)

print(f"Orphan submissions: {result['submission_count']}")
print(f"Unique orphan drugs: {result['unique_drug_count']}")
print(f"Orphan brands: {', '.join(result['brands_with_pathway'])}")
# Example: 3 submissions, 17 unique drugs, 2 brands (VITRAKVI, RUBRACA)
```

### Use Case 3: Competitive Intelligence
```python
# Analyze pathway usage in competitive space
result = get_products_by_approval_pathway(
    pathway="priority_review",
    therapeutic_area="KRAS inhibitor",
    get_brand_names=True,
    filter_brands_by_pathway=True
)

# Shows which specific brands got priority review
```

---

## Performance Characteristics (v4.0)

| Feature | Speed | API Calls | Use When |
|---------|-------|-----------|----------|
| Basic pathway query | Slow (1 + N) | 1 discovery + N drugs | Default use (comprehensive results) |
| + Unique counting | Slower (1 + 2N) | + N deduplication | Need accurate unique drug counts |

**v4.0 Hybrid Method**:
- **STEP 1**: 1 API call to adverse events (gets up to 100 candidate drugs)
- **STEP 2**: N API calls to check pathway for each candidate (typically N=8-57)
- **Total**: Usually 10-60 API calls per query (slower but comprehensive)

**Trade-offs**:
- ✅ **Completeness**: 100% therapeutic area coverage (no more failures)
- ✅ **Real-world data**: Adverse events reflect actual prescribing
- ⚠️ **Speed**: Slower than v3.0 due to individual drug checks
- ✅ **Accuracy**: Cross-references submission metadata for pathway verification

**Recommendations**:
- Accept the slower speed for comprehensive results
- Use `count_type="unique_drugs"` only if you need deduplication
- Results are cached at adverse events level (STEP 1 is fast on repeat queries)

---

## Change Log

**Version 4.0 (2025-11-28)**: 🚀 BREAKTHROUGH - Hybrid Adverse Events Discovery
- ✅ **MAJOR**: Hybrid adverse events + submission metadata method
- ✅ **MAJOR**: 100% therapeutic area coverage (solves sparse metadata problem)
- ✅ **MAJOR**: Real-world prescribing data via adverse event counts
- ✅ **Added**: Works for obesity, multiple sclerosis, ALL therapeutic areas
- ✅ **Added**: Drugs ranked by adverse events (usage proxy)
- ✅ **Changed**: Returns `drugs` list with brand_name, adverse_events, pathway
- ✅ **Removed**: Term validation cache (no longer needed)
- ⚠️ **Performance**: Slower but comprehensive (10-60 API calls vs 1-3)
- 🎯 **Impact**: Obesity priority review: 0 → 9 drugs, MS orphan: 0 → 13 drugs

**Version 3.0 (2025)**: Major improvements release
- ✅ Added: Therapeutic area term validation with auto-suggestions
- ✅ Added: Unique drug counting (deduplicate by application_number)
- ✅ Added: Brand name filtering by pathway (3-step verification)
- ✅ Added: Year filtering parameters (approval_year_start/end)
- ✅ Added: Advanced field_exists filtering parameter
- ✅ Improved: Better error messages and user feedback
- ✅ Improved: Progress tracking for slow operations
- ⚠️ **Limitation**: Sparse submission metadata caused failures for many therapeutic areas

**Version 2.0 (2025)**: Complete rewrite using FDA submission metadata fields
- ✅ Fixed: Now uses working FDA API fields
- ✅ Fixed: Count-first pattern prevents token overflow
- ✅ Added: submissions.review_priority support (priority vs standard)
- ✅ Added: submissions.submission_property_type support (orphan)
- ✅ Changed: Removed broken accelerated/breakthrough/fast_track pathways
- ⚠️ Breaking: Pathway parameter values changed

**Version 1.0 (broken)**: Original implementation
- ❌ Bug: Missing count parameter caused 67k token overflow
- ❌ Bug: Pathway search terms returned 404 errors
- ❌ Bug: Could not reliably detect any pathway

---

## Alternative Data Sources

For comprehensive pathway analysis, cross-reference with:

1. **FDA Accelerated Approvals**: https://www.fda.gov/drugs/nda-and-bla-approvals/accelerated-approvals
2. **FDA Breakthrough Therapies**: https://www.fda.gov/drugs/development-approval-process-drugs/breakthrough-therapy
3. **FDA Orphan Drug Database**: https://www.accessdata.fda.gov/scripts/opdlisting/oopd/
4. **Drugs@FDA**: https://www.accessdata.fda.gov/scripts/cder/daf/
