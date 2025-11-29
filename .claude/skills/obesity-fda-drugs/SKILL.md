---
name: get_obesity_fda_drugs
description: >
  Discovers FDA-approved obesity drugs dynamically using the adverse events database.
  Queries the patient.drug.drugindication field for obesity-related terms (obesity,
  weight control, overweight) to identify drugs prescribed for obesity treatment.
  Filters results to drugs with significant obesity-specific adverse event reports
  (>=400 reports or >=25% obesity ratio) to eliminate incidental mentions.
  Returns real-world usage data showing which drugs are actually prescribed for obesity.

  This method solves the FDA vocabulary discovery problem by leveraging adverse events
  data where patient indications are captured from real prescriptions.

  Trigger keywords: obesity drugs, weight loss drugs, obesity medications, FDA approved
  obesity, weight management drugs, obesity treatment drugs
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - adverse_events_discovery
  - count_pattern
  - indication_filtering
data_scope:
  total_results: ~10-15 primary obesity drugs
  geographical: US only
  temporal: All time (based on adverse event reports)
created: 2025-11-28
last_updated: 2025-11-28
complexity: medium
execution_time: ~8 seconds
token_efficiency: ~99.5% reduction vs raw adverse events data
---

# get_obesity_fda_drugs

## Purpose
Discovers all FDA-approved obesity drugs in the United States by querying the adverse events database for real-world prescription patterns. Unlike label-based searches (which fail due to token limits), this approach uses the `patient.drug.drugindication` field to find drugs where "obesity" or related terms appear as the reported indication.

## Key Innovation
This skill solves the FDA therapeutic area vocabulary discovery problem using a novel approach:

**Traditional Approach** (doesn't work):
- ❌ Search drug labels for "obesity" → 67k tokens → Exceeds MCP limit → Fails
- ❌ Field selection broken → Cannot filter label fields
- ❌ Count queries don't work on free text

**Our Approach** (works):
- ✅ Query adverse events database: `patient.drug.drugindication:obesity`
- ✅ Count by brand name: `count=patient.drug.openfda.brand_name.exact`
- ✅ Filter to drugs with significant obesity indication (>=400 reports or >=25% ratio)
- ✅ Discovers obesity drugs dynamically without hardcoded lists

## Usage
Use when you need to:
- Find all FDA-approved obesity/weight loss drugs
- Understand real-world obesity drug prescribing patterns
- Compare obesity drug usage by adverse event volume
- Discover obesity drugs without maintaining hardcoded drug lists

## Implementation Details

### Step 1: Multi-Term Search
Searches three obesity-related indication terms:
- `"obesity"` - Primary obesity indication
- `"weight control"` - Weight management/maintenance
- `"overweight"` - Overweight treatment

### Step 2: Count Aggregation
For each term, counts adverse event reports by brand name:
```python
lookup_drug(
    search_term="patient.drug.drugindication:obesity",
    search_type="adverse_events",
    count="patient.drug.openfda.brand_name.exact",
    limit=100
)
```

### Step 3: Smart Filtering
Filters results to drugs with **significant obesity indication**:
- **Rule 1**: >= 400 obesity-specific adverse event reports, OR
- **Rule 2**: Obesity reports >= 25% of total reports

This eliminates noise from drugs that mention "obesity" incidentally (e.g., pain relievers reported alongside obesity as comorbidity).

### Step 4: Ranking
Sorts by obesity-specific report count (highest first) to show most commonly prescribed obesity drugs.

## Data Structure
Returns dictionary with:
- `drugs`: List of drug dictionaries
- `total_count`: Number of obesity drugs found
- `summary`: Formatted string output

Each drug dictionary contains:
- `brand_name`: Brand name
- `obesity_events`: Obesity-specific adverse event count
- `total_adverse_events`: All adverse events across all indications
- `indications`: Dict mapping indication terms to their counts
  - `obesity`: Count from obesity-specific reports
  - `weight control`: Count from weight control reports
  - `overweight`: Count from overweight reports

## Example Output
```
FDA-Approved Obesity Drugs in the US

Total drugs found: 11

(Filtered to drugs with significant obesity indication)


Drugs by Obesity-Specific Usage:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WEGOVY
   Obesity-Specific Reports: 1,550
   Total Reports: 1,920
   All Indications: obesity(1,550), overweight(370)

2. XENICAL
   Obesity-Specific Reports: 1,474
   Total Reports: 1,633
   All Indications: obesity(1,474), overweight(159)

3. OZEMPIC
   Obesity-Specific Reports: 1,400
   Total Reports: 1,561
   All Indications: obesity(1,400), overweight(161)

4. SAXENDA
   Obesity-Specific Reports: 1,012
   Total Reports: 1,207
   All Indications: obesity(1,012), overweight(195)

5. ALLI
   Obesity-Specific Reports: 819
   Total Reports: 876
   All Indications: obesity(819), overweight(57)

6. ORLISTAT
   Obesity-Specific Reports: 767
   Total Reports: 767
   All Indications: obesity(767)

7. METFORMIN HYDROCHLORIDE
   Obesity-Specific Reports: 708
   Total Reports: 821
   All Indications: obesity(708), overweight(113)

8. METFORMIN
   Obesity-Specific Reports: 609
   Total Reports: 706
   All Indications: obesity(609), overweight(97)

9. CONTRAVE EXTENDED-RELEASE
   Obesity-Specific Reports: 608
   Total Reports: 1,335
   All Indications: obesity(608), overweight(727)

10. MOUNJARO
   Obesity-Specific Reports: 544
   Total Reports: 619
   All Indications: obesity(544), overweight(75)
```

## Notes
- **Data Source**: FDA Adverse Events Reporting System (FAERS)
- **Indication Capture**: The `patient.drug.drugindication` field captures the condition for which a drug was prescribed when an adverse event was reported
- **Real-World Usage**: Adverse event counts reflect real-world prescribing volume (more reports = more widely prescribed)
- **Not Approval Status**: This discovers drugs prescribed for obesity, not necessarily FDA-approved specifically for obesity (e.g., OZEMPIC is approved for diabetes but widely prescribed off-label for weight loss)
- **Filtering Necessary**: Without filtering, results include many non-obesity drugs (pain relievers, etc.) that appear in reports mentioning obesity as a comorbidity
- **Limitation**: Captures reported adverse events only - drugs without adverse event reports won't appear
- **GLP-1 Drugs**: Includes both FDA-approved obesity drugs (Wegovy, Saxenda) and diabetes drugs prescribed off-label for weight loss (Ozempic, Mounjaro)

## References
- FDA Adverse Events API: https://open.fda.gov/apis/drug/event/
- `patient.drug.drugindication` field: Free-text indication from adverse event reports
- Discovery method: Uses count aggregation on adverse events (avoids label token overflow)
