---
name: get_safety_stopped_trials
description: >
  Find clinical trials stopped due to safety concerns for any indication.
  Searches CT.gov "Why Stopped" field with safety keywords (death, toxicity, SAE, etc.).

  Provides comprehensive safety intelligence:
  - Trial-level details with actual "Why Stopped" text
  - Notable drug failures with automated severity scoring
  - Phase/status/condition breakdown
  - Sponsor attribution with major pharma identification

  Use when you need:
  - Safety red flags for therapeutic area
  - Drug failure analysis (discontinued programs)
  - Competitive safety intelligence
  - Due diligence for acquisitions (safety risk assessment)

  Generic skill parameterized by indication - works for any disease.
category: safety-intelligence
mcp_servers:
  - ct_gov_mcp
patterns:
  - focused_query
  - safety_keyword_scoring
  - drug_failure_analysis
  - multi_keyword_search
data_scope:
  total_results: Full analysis (all matching safety-stopped trials)
  geographical: Global
  temporal: All stopped trials (terminated, withdrawn, suspended)
created: 2025-11-28
last_updated: 2025-11-28
complexity: moderate
execution_time: ~30-90 seconds (depends on indication size)
token_efficiency: ~99% reduction
---
# get_safety_stopped_trials


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for safety stopped?`
2. `@agent-pharma-search-specialist Find active safety stopped trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for safety stopped`


## Purpose

Generic safety intelligence tool to identify clinical trials stopped due to safety concerns for any therapeutic area.

Focuses on:
- Automated safety keyword detection in "Why Stopped" field
- Drug failure scoring (trial count + phase + sponsor + severity)
- Actual "Why Stopped" text extraction (transparency)
- Condition subtype categorization (optional)

## Usage

**Direct execution**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/safety-stopped-trials/scripts/get_safety_stopped_trials.py "diabetes"

# With condition subtypes
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/safety-stopped-trials/scripts/get_safety_stopped_trials.py "cancer" "{'lung': ['nsclc', 'small cell'], 'breast': ['triple negative', 'her2+']}"
```

**Import and use**:
```python
from skills.safety_stopped_trials.scripts.get_safety_stopped_trials import get_safety_stopped_trials

# Basic usage
result = get_safety_stopped_trials("NSCLC")
print(f"Total safety-stopped trials: {result['total_count']}")
print(f"Top failed drug: {result['notable_drugs'][0]['drug_name']}")

# With condition subtypes
subtypes = {
    'Type 1': ['type 1', 'type i', 't1d'],
    'Type 2': ['type 2', 'type ii', 't2d'],
    'Gestational': ['gestational', 'gdm']
}
result = get_safety_stopped_trials("diabetes", condition_subtypes=subtypes)
print(f"By subtype: {result['categorizations']['by_condition_subtype']}")
```

## Parameters

- `indication` (required): Disease/therapeutic area (e.g., "diabetes", "NSCLC", "obesity")
- `condition_subtypes` (optional): Dict mapping subtype labels to keyword lists for categorization
  - Example: `{'Type 1': ['type 1', 't1d'], 'Type 2': ['type 2', 't2d']}`
  - If None, categorizes as "Other/Unspecified"

## Output Structure

Returns dict with:
- `indication`: Indication queried
- `total_count`: Total number of safety-stopped trials
- `trials`: List of trial details:
  - `nct_id`: NCT identifier
  - `title`: Study title
  - `status`: Overall status (Terminated, Withdrawn, Suspended)
  - `why_stopped`: Actual "Why Stopped" text from CT.gov
  - `interventions`: Drug/biological interventions
  - `phase`: Clinical phase
  - `conditions`: Conditions studied
  - `sponsor`: Lead sponsor
  - `link`: ClinicalTrials.gov URL
- `categorizations`:
  - `by_phase`: Trial count by phase
  - `by_condition_subtype`: Trial count by condition subtype (if provided)
  - `by_status`: Trial count by status
- `notable_drugs`: Scored drug failures (sorted by total score):
  - `drug_name`: Drug name
  - `trial_count`: Number of trials
  - `nct_ids`: List of NCT IDs
  - `max_phase`: Most advanced phase reached
  - `sponsors`: Sponsor names
  - `safety_keywords`: Safety keywords detected
  - `why_stopped_examples`: Actual "Why Stopped" text (up to 3 examples)
  - `scores`: Breakdown by criterion:
    - `trial_count`: 3+ = 10pts | 2 = 5pts | 1 = 1pt
    - `phase`: Phase 3/4 = 10pts | Phase 2 = 6pts | Phase 1 = 3pts
    - `major_pharma`: Yes = 10pts | No = 0pts
    - `safety_severity`: Death = 10pts | Toxicity = 8pts | SAE = 5pts | etc.
  - `total_score`: Sum of all scores
- `summary`: Human-readable formatted summary

## Example Output

```
================================================================================
DIABETES TRIALS STOPPED DUE TO SAFETY CONCERNS
================================================================================

Total Trials: 156

Status Breakdown:
  • Terminated: 128 trials
  • Withdrawn: 21 trials
  • Suspended: 7 trials

Phase Breakdown:
  • Phase 2: 58 trials
  • Phase 1: 42 trials
  • Phase 3: 31 trials
  • N/A: 15 trials
  • Phase 4: 10 trials

Condition Subtype Breakdown:
  • Type 2 Diabetes: 89 trials
  • Type 1 Diabetes: 42 trials
  • Gestational Diabetes: 11 trials
  • Other/Unspecified: 14 trials

================================================================================
NOTABLE DRUG FAILURES - AUTOMATICALLY SCORED
================================================================================

Scoring Criteria:
  • Trial Count: 3+ trials = 10pts | 2 trials = 5pts | 1 trial = 1pt
  • Phase: Phase 3/4 = 10pts | Phase 2 = 6pts | Phase 1 = 3pts | N/A = 0pts
  • Major Pharma: Yes = 10pts | No = 0pts
  • Safety Severity: Death/Fatal = 10pts | Toxicity = 8pts | Adverse = 5pts

Rank  Drug Name                      Trials  Phase      Pharma  Severity  TOTAL  Sponsors
================================================================================
1     Muraglitazar                   10      10         10      8         38     Bristol-Myers Squibb, Merck
2     Ragaglitazar                   5       10         10      8         33     Novo Nordisk
3     Fasiglifam                     5       10         10      5         30     Takeda
...

================================================================================
ACTUAL 'WHY STOPPED' REASONS FOR TOP DRUGS
================================================================================

1. Muraglitazar (Score: 38, 3 trials)
   • NCT00123456: Cardiovascular toxicity concerns identified
   • NCT00234567: Increased mortality in treatment arm
   • NCT00345678: Hepatotoxicity and adverse cardiovascular events

2. Ragaglitazar (Score: 33, 2 trials)
   • NCT00456789: Bladder cancer signal detected
   • NCT00567890: Serious adverse events including carcinogenicity
```

## Safety Keyword Scoring

The skill searches for 12 safety keywords in the "Why Stopped" field, each with severity weighting:

| Keyword | Severity Score | Examples |
|---------|----------------|----------|
| death, mortality, fatal | 10 | Increased mortality, fatal adverse events |
| toxicity, toxic, hepatotoxicity | 8 | Hepatotoxicity, cardiotoxicity, dose-limiting toxicity |
| adverse, SAE, serious adverse | 5 | Serious adverse events, unacceptable adverse effects |
| tolerability, side effect, intolerable | 3 | Poor tolerability, intolerable side effects |
| safety, harm, hypoglycemia | 1 | Safety concerns, potential harm |

**Drug Scoring Algorithm**:
1. **Trial Count** (1-10pts): More failed trials = higher risk
2. **Phase** (0-10pts): Later phase = greater investment loss
3. **Major Pharma** (0-10pts): Big pharma failure = notable signal
4. **Safety Severity** (0-10pts): Death/toxicity > tolerability

Total Score Range: 0-38 points (higher = more notable failure)

## When to Use This vs diabetes-drugs-stopped-safety

| Feature | This Skill (generic) | diabetes-drugs-stopped-safety (legacy) |
|---------|---------------------|----------------------------------------|
| Indication | Any (parameterized) | Diabetes only (hardcoded) |
| Subtypes | Optional (flexible) | Diabetes subtypes (hardcoded) |
| Reusability | ✓ All therapeutic areas | ✗ Diabetes only |
| Recommended | ✓ Use this | ⚠️ Legacy (keep for backward compatibility) |

## Implementation Details

### Core Strategy

1. **Multi-keyword search** of CT.gov "Why Stopped" field
2. **Union of NCT IDs** across all safety keywords (death, toxicity, SAE, etc.)
3. **Fetch trial details** for all matched trials (get_study API)
4. **Parse "Why Stopped"** text from each trial
5. **Score drugs** based on trial count, phase, sponsor, severity
6. **Categorize** by phase, status, condition subtype (optional)

### Condition Subtype Categorization

Optional parameter `condition_subtypes` enables disease-specific breakdown:

```python
# Example: Diabetes
condition_subtypes = {
    'Type 1 Diabetes': ['type 1', 'type i', 't1d'],
    'Type 2 Diabetes': ['type 2', 'type ii', 't2d'],
    'Gestational Diabetes': ['gestational', 'gdm']
}

# Example: Cancer
condition_subtypes = {
    'NSCLC': ['non-small cell', 'nsclc'],
    'SCLC': ['small cell', 'sclc'],
    'Adenocarcinoma': ['adenocarcinoma', 'adc']
}

# If None: All categorized as "Other/Unspecified"
```

### Major Pharma List

Automatically identifies major pharma sponsors for scoring:
- Pfizer, Novartis, Roche, Merck, GSK, Sanofi, AbbVie, Takeda, Bayer, Biogen, Amgen
- Bristol-Myers Squibb, Eli Lilly, Johnson & Johnson, AstraZeneca, Boehringer Ingelheim
- Novo Nordisk, Regeneron

## Limitations

1. **Text-based search**: "Why Stopped" field is free text (no controlled vocabulary)
2. **Keyword coverage**: May miss synonyms not in keyword list
3. **False positives**: Some keywords may appear in non-safety contexts
4. **Manual subtype definition**: User must provide condition subtype mappings

## Related Skills

- **diabetes-drugs-stopped-safety**: Legacy diabetes-specific version (use this generic skill instead)
- **get_clinical_trials**: Basic trial search (no safety focus)
- **companies-by-moa**: Company landscape (doesn't track safety failures)

## Verification

Verified with:
- ✅ Execution: Clean exit, no errors
- ✅ Data retrieved: Safety-stopped trials extracted
- ✅ Parameterization: Works with diabetes, cancer, NSCLC
- ✅ Executable: Standalone with `if __name__`
- ✅ Schema: Valid trial structure with "why_stopped" field
- ✅ Drug scoring: Automated ranking by multiple criteria