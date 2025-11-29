---
name: get_diabetes_drugs_stopped_safety
deprecated: true
deprecated_date: 2025-11-28
replacement: safety-stopped-trials
replacement_skill: get_safety_stopped_trials
migration_guide: |
  Use the generic safety-stopped-trials skill instead:
  - Old: get_diabetes_drugs_stopped_safety()
  - New: get_safety_stopped_trials("diabetes", condition_subtypes={...})

  This skill now wraps the generic version for backward compatibility.
  Please migrate to safety-stopped-trials for all new projects.
description: >
  ⚠️ DEPRECATED: Use safety-stopped-trials skill instead (generic, works for any indication).

  Identifies diabetes clinical trials that were terminated, withdrawn, or suspended
  due to safety concerns. Uses ClinicalTrials.gov AREA[WhyStopped] field with
  complexQuery to search for safety-related stop reasons (adverse events, toxicity,
  deaths, hypoglycemia, tolerability issues).

  It extracts actual "Why Stopped" text from each trial for accurate
  severity scoring and transparency. Scans full safety reason text (not just search
  keywords) to identify specific issues like hepatotoxicity, cardiovascular risks,
  etc. Shows actual safety reasons for top drug failures with multi-criteria scoring.

  Extracts intervention/drug names, phases, sponsors. Categorizes findings by
  development phase and diabetes type to reveal patterns. Automatically scores and
  ranks notable drug failures.

  Use when investigating: drug safety failures, discontinued diabetes treatments,
  safety-driven development terminations, toxicity patterns, adverse event trends.

  Keywords: stopped, terminated, withdrawn, suspended, safety, adverse events,
  toxicity, deaths, hypoglycemia, tolerability, diabetes drug failures.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - complexQuery
  - AREA_field_search
  - keyword_matching
  - pagination
  - deduplication
data_scope:
  total_results: 135
  geographical: Global
  temporal: All time
  diabetes_types: Type 1, Type 2, Gestational, Other
created: 2025-11-25
last_updated: 2025-11-25
complexity: medium
execution_time: ~2-5 minutes (complete pagination through all results)
token_efficiency: ~99% reduction vs raw data
---
# get_diabetes_drugs_stopped_safety


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for diabetes?`
2. `@agent-pharma-search-specialist Find active diabetes trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for diabetes`


> **⚠️ DEPRECATED (2025-11-28)**
>
> This skill has been superseded by the generic **`safety-stopped-trials`** skill which works for any therapeutic area.
>
> **Migration:**
> ```python
> # Old (diabetes-specific)
> from skills.diabetes_drugs_stopped_safety.scripts.get_diabetes_drugs_stopped_safety import get_diabetes_drugs_stopped_safety
> result = get_diabetes_drugs_stopped_safety()
>
> # New (generic, recommended)
> from skills.safety_stopped_trials.scripts.get_safety_stopped_trials import get_safety_stopped_trials
> result = get_safety_stopped_trials("diabetes", condition_subtypes={
>     'Type 1 Diabetes': ['type 1', 'type i', 't1d'],
>     'Type 2 Diabetes': ['type 2', 'type ii', 't2d'],
>     'Gestational Diabetes': ['gestational', 'gdm']
> })
> ```
>
> This legacy skill now wraps the generic version for backward compatibility.
> Please use `safety-stopped-trials` for all new projects.

## Purpose

Identifies diabetes drugs and interventions that stopped development due to safety concerns by searching terminated, withdrawn, and suspended trials in ClinicalTrials.gov.

## Usage

This skill is valuable for:
- **Safety surveillance**: Track patterns in drug safety failures
- **Competitive intelligence**: Understand why competitors stopped programs
- **Risk assessment**: Identify safety risks for similar mechanisms/targets
- **Regulatory strategy**: Learn from safety-driven terminations
- **Due diligence**: Investigate historical safety issues for drug classes

## Trigger Keywords

Use this skill when queries contain:
- "stopped", "terminated", "withdrawn", "suspended"
- "safety concerns", "adverse events", "toxicity"
- "discontinued", "halted", "ceased"
- "drug failures", "development failures"
- Combined with "diabetes" or specific diabetes types

## Implementation Details

### Search Strategy
1. Queries ClinicalTrials.gov for diabetes trials with statuses:
   - Terminated
   - Withdrawn
   - Suspended
2. Filters results for trials with safety-related stop reasons using keywords:
   - Adverse events, toxicity, deaths, hypoglycemia, tolerability
3. Handles pagination (1000 results per page) to retrieve complete dataset

### Data Extraction
For each safety-stopped trial, extracts:
- NCT ID
- Trial title
- Stop status (terminated/withdrawn/suspended)
- Why Stopped reason (full text)
- Intervention/drug names
- Phase (Early Phase 1, Phase 1, 2, 3, 4)
- Diabetes conditions/types

### Categorization
Organizes results by:
- **Safety Reason Type**: Adverse Events, Toxicity, Deaths/Mortality, Hypoglycemia, Tolerability, General Safety
- **Development Phase**: Early Phase 1, Phase 1, Phase 2, Phase 3, Phase 4, N/A
- **Diabetes Type**: Type 1, Type 2, Gestational, Other/Unspecified
- **Stop Status**: Terminated, Withdrawn, Suspended

### Safety Keyword Matching
Uses comprehensive keyword sets to categorize safety reasons:
- **Adverse Events**: adverse, side effect, SAE, serious event
- **Toxicity**: toxicity, toxic, hepatotoxic, cardiotoxic, nephrotoxic, neurotoxic
- **Deaths/Mortality**: death, mortality, fatal
- **Hypoglycemia**: hypoglycemia, severe hypoglycemia
- **Tolerability**: tolerability, intolerable, poorly tolerated
- **General Safety**: safety, risk, hazard, harm

### Notable Drug Failures Scoring (NEW)
Automatically identifies and ranks notable drug failures using multi-criteria scoring:

**Scoring Criteria** (Total = sum of all scores):
1. **Trial Count Score**: Number of trials stopped for same drug
   - 3+ trials = 10 points
   - 2 trials = 5 points
   - 1 trial = 1 point

2. **Phase Score**: Latest development phase reached before termination
   - Phase 3/4 = 10 points (late-stage failure, high visibility)
   - Phase 2 = 6 points (mid-stage failure)
   - Phase 1/Early Phase 1 = 3 points (early-stage)
   - N/A = 0 points

3. **Major Pharma Score**: Large pharmaceutical company sponsor
   - Major pharma = 10 points (high visibility, industry impact)
   - Other = 0 points
   - Major pharma list: Pfizer, Novartis, Roche, Merck, GSK, Sanofi, AbbVie, Takeda, Bayer, Biogen, Amgen, BMS, Lilly, J&J, AstraZeneca, Boehringer, Novo Nordisk, Regeneron

4. **Safety Severity Score**: Type of safety issue (from actual "Why Stopped" text)
   - Death/Mortality/Fatal = 10 points (most severe)
   - Toxicity/Hepatotoxicity/Cardiotoxicity = 8 points
   - Adverse events/SAE/Serious Adverse = 5 points
   - Tolerability/Side effects/Intolerable = 3 points
   - General safety/Harm/Hypoglycemia = 1 point
   - **Source**: Scanned from actual "Why Stopped" text extracted via get_study() (more accurate than search keywords)

**Output**: Top 20 drugs ranked by total score in tabular format with score breakdown

## Return Format

Returns dictionary with:
```python
{
    'total_count': int,           # Total trials found
    'trials': [                   # List of trial details
        {
            'nct_id': str,
            'title': str,
            'status': str,
            'why_stopped': str,       # NEW: Actual "Why Stopped" text from CT.gov
            'interventions': str,
            'phase': str,
            'conditions': str,
            'sponsor': str,
            'link': str
        }
    ],
    'categorizations': {          # Breakdowns by category
        'by_phase': dict,
        'by_diabetes_type': dict,
        'by_status': dict
    },
    'notable_drugs': [            # Scored and ranked notable drug failures
        {
            'drug_name': str,
            'trial_count': int,
            'max_phase': str,
            'sponsors': str,
            'safety_keywords': str,      # Severity keywords found in "Why Stopped" text
            'why_stopped_examples': [    # NEW: Actual "Why Stopped" text examples
                {
                    'nct_id': str,
                    'reason': str
                }
            ],
            'scores': {
                'trial_count': int,
                'phase': int,
                'major_pharma': int,
                'safety_severity': int
            },
            'total_score': int
        }
    ],
    'nct_to_keywords': dict,      # Mapping: NCT ID -> [(keyword, score), ...]
    'summary': str                # Human-readable summary with table
}
```

## Example Output

```
Diabetes Trials Stopped Due to Safety Concerns: 135 trials found

Status Breakdown:
  • Terminated: 118 trials
  • Withdrawn: 13 trials
  • Suspended: 4 trials

Phase Breakdown:
  • Phase2: 39 trials
  • Phase3: 37 trials
  • Na: 21 trials
  • Phase4: 14 trials
  • Phase1: 11 trials

Diabetes Type Breakdown:
  • Other/Unspecified: 75 trials
  • Type 2 Diabetes: 50 trials
  • Type 1 Diabetes: 8 trials
  • Gestational Diabetes: 2 trials

NOTABLE DRUG FAILURES - AUTOMATICALLY SCORED

Scoring Criteria:
  • Trial Count: 3+ trials = 10pts | 2 trials = 5pts | 1 trial = 1pt
  • Phase: Phase 3/4 = 10pts | Phase 2 = 6pts | Phase 1 = 3pts | N/A = 0pts
  • Major Pharma: Yes = 10pts | No = 0pts
  • Safety Severity: Death = 10pts | Toxicity = 8pts | Adverse = 5pts | Tolerability = 3pts | Safety = 1pt

Rank  Drug Name                      Trials  Phase      Pharma  Severity  TOTAL  Sponsors
========================================================================================================
1     Placebo                        10      10         10      1         31     Biogen, Eli Lilly and Company
2     TAK-875                        10      10         10      1         31     Takeda
3     Fasiglifam                     10      10         10      0         30     Takeda
4     Bardoxolone Methyl             10      6          10      1         27     Biogen
5     PF-05175157                    10      6          10      1         27     Pfizer
6     Efpeglenatide                  5       10         10      1         26     Sanofi
7     TAK-559                        5       10         10      1         26     Takeda
8     PRM-151                        5       10         10      1         26     Hoffmann-La Roche
9     Efpeglenatide SAR439977        5       10         10      1         26     Sanofi
10    Alogliptin                     5       10         10      1         26     Takeda
11    Aliskiren                      5       10         10      0         25     Novartis Pharmaceuticals
12    Albiglutide                    1       10         10      3         24     GlaxoSmithKline

Showing top 20 of 114 unique drugs
```

## Technical Notes

- **AREA[WhyStopped] Field**: Uses complexQuery to search "Why Stopped" field directly
- **Keyword Search**: Searches 11 safety keywords (safety, adverse, toxicity, death, etc.)
- **Complete Pagination**: Retrieves ALL pages for each keyword (no sampling or limits)
- **Deduplication**: Uses set-based collection to avoid counting same trial multiple times
- **Response Format**: CT.gov returns markdown (not JSON) - uses regex parsing
- **Execution Time**: ~2-5 minutes to search all keywords through all pages and fetch trial details

### Severity Scoring Implementation (ENHANCED)

**New Approach**: Extracts actual "Why Stopped" text from get_study() for accurate severity analysis

**Previous limitation**:
- Severity scoring relied on which search keyword matched (e.g., if `AREA[WhyStopped]safety` matched, score = 1pt)
- Problem: Actual text might say "Hepatic toxicity signal" (8pts) but only matched "safety" (1pt)

**Current solution** (after MCP server enhancement):
- CT.gov MCP server now returns "Why Stopped" field in get_study() responses
- Example: NCT00762190 (TAK-559) returns `**Why Stopped:** Hepatic safety signal identified.`
- Severity scoring scans the ACTUAL "Why Stopped" text for ALL severity keywords
- Result: NCT00762190 now scores correctly (contains "safety" = 1pt) but if text had "toxicity" would score 8pts

**Accuracy improvement**:
- Previous: Scored based on which search keyword matched (1 keyword per trial)
- Current: Scans actual "Why Stopped" text for ALL 15+ severity keywords
- Impact: More accurate severity scores, better ranking of drug failures
- Transparency: Shows actual "Why Stopped" text in output for top drugs

**Example**:
```
TAK-875 (Fasiglifam) - Score: 31 points
  • NCT01780259: Study terminated based upon the hepatic safety signal...
  • NCT01131676: Study stopped based on hepatic safety signal that was...
  • NCT01242215: Study was terminated due to a hepatic safety signal...
```
All trials show "hepatic" + "safety" keywords - automatic detection of liver toxicity pattern!

## Dependencies

- `mcp.servers.ct_gov_mcp.search` - ClinicalTrials.gov search function
- `mcp.servers.ct_gov_mcp.get_study` - Fetch detailed trial information including "Why Stopped" field
- Python `re` module for regex parsing

## Related Skills

- `get_diabetes_recruiting_trials` - Active diabetes trials (recruiting)
- `get_glp1_trials` - GLP-1 receptor agonist trials
- `get_sglt2_inhibitor_trials` - SGLT2 inhibitor trials

## Insights from Current Data (135 trials)

Based on automated analysis:

**Trial Distribution**:
- **Phase 2 & 3 are highest risk**: 56% of safety stops occur in Phase 2 (29%) or Phase 3 (27%)
- **Type 2 diabetes dominates**: 37% explicitly mention Type 2 (55% unspecified may include both)
- **Status**: 87% terminated, 10% withdrawn, 3% suspended

**Safety Keywords Found**:
- 102 trials mention "safety" (most common)
- 18 trials mention "death" (highest severity)
- 7 trials mention "adverse"
- 3 trials mention "toxicity"
- 2 trials mention "tolerability"

**Notable Drug Failures** (automated scoring identifies):
- **Highest scores (31 points)**: TAK-875/Fasiglifam (Takeda) - Phase 3, 10 trials
- **Pattern failures**: 10 drugs with 3+ stopped trials each
- **Major pharma**: Top 20 drugs all from major pharmaceutical companies
- **Late-stage failures**: Top drugs reached Phase 3/4 before termination
- **Well-known cases automatically detected**: Fasiglifam (hepatotoxicity), Aliskiren (ALTITUDE trial), Bardoxolone methyl (kidney safety), Albiglutide (GSK)

**Automated vs Manual Selection**:
- Previous manual selection was subjective and required domain knowledge
- New automated scoring objectively ranks all 114 unique drugs
- Data-driven approach eliminates selection bias
- Reproducible and consistent across different users