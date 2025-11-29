# Trial Completion Predictor


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for trial-completion-predictor?`
2. `@agent-pharma-search-specialist Find active trial-completion-predictor trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for trial-completion-predictor`


## Overview

Predicts likely conference presentations based on ClinicalTrials.gov trial completion dates and conference timing. Uses therapeutic area matching and completion timing windows to identify trials likely to present data.

**Key Catalyst**: Predicted presentations allow proactive positioning 2-4 months before conferences.

## How Trial-to-Conference Prediction Works

When a Phase 2/3 trial completes, companies typically present results at the next relevant therapeutic area conference within 3-9 months.

**Prediction Logic:**
```
Trial completes → Data analysis (2-3 months) → Abstract submission (3-4 months before conference) → Conference presentation
```

**Timing Windows:**
- **Optimal**: Trial completion 3-9 months before conference
- **Too Early**: > 9 months (likely presented at previous conference)
- **Too Late**: < 3 months (abstract deadline passed)

## Therapeutic Area to Conference Mapping

| Therapeutic Area | Primary Conference | Timing | Secondary |
|------------------|-------------------|--------|-----------|
| Multiple Myeloma, Leukemia, Lymphoma | ASH | December | EHA (June) |
| Solid Tumors (all) | ASCO | June | ESMO (Sept) |
| Diabetes, Obesity | ADA | June | EASD (Sept) |
| Alzheimer's, Dementia | CTAD | Oct/Nov | AAIC (July) |
| Cardiovascular | ACC | March | AHA (Nov) |
| All Cancers (research) | AACR | April | - |

## How It Works

1. **Get completed trials** from ClinicalTrials.gov for target companies
2. **Filter by completion date** (3-9 months before target quarter conferences)
3. **Match therapeutic area** to appropriate conference
4. **Calculate presentation probability** based on timing and trial phase
5. **Return predicted presentations** with confidence scores

## Data Source

**ClinicalTrials.gov** - Trial completion dates and therapeutic areas

No 8-K filing required - purely algorithmic prediction based on:
- Trial completion dates
- Therapeutic area
- Conference schedules
- Historical presentation patterns

## Expected Results (Q4 2025 Example)

**Input**: Q4 2025 (Oct-Dec 2025)

**Output**: ~20-30 predicted presentations

Example:
```
| Company | Drug | Indication | Trial | Completed | Conference | Probability |
|---------|------|------------|-------|-----------|------------|-------------|
| BMS | Ide-cel | Multiple Myeloma | NCT12345678 | May 2025 | ASH 2025 | 85% |
| Lilly | Donanemab | Alzheimer's | NCT98765432 | Jul 2025 | CTAD 2025 | 75% |
| ... | ... | ... | ... | ... | ... | ... |
```

## Usage

```python
from .claude.skills.trial_completion_predictor.scripts.predict_trial_presentations import predict_trial_presentations

# Predict presentations for Q4 2025
result = predict_trial_presentations(
    quarter="Q4",
    year=2025,
    min_probability=0.6  # Only return predictions with >= 60% confidence
)

# Result:
{
    'quarter': 'Q4 2025',
    'total_predictions': 24,
    'predictions': [
        {
            'company': 'BMS',
            'drug': 'Ide-cel',
            'indication': 'Multiple Myeloma',
            'trial_id': 'NCT12345678',
            'trial_phase': 'PHASE3',
            'completion_date': '2025-05-15',
            'conference': 'ASH 2025',
            'conference_dates': '2025-12-07 to 2025-12-10',
            'presentation_probability': 0.85,
            'confidence_reason': 'Optimal timing (7 months post-completion)',
            'therapeutic_area_match': 'Blood Cancer → ASH'
        },
        # ... 23 more
    ],
    'summary': {
        'total': 24,
        'by_conference': {'ASH': 10, 'CTAD': 8, 'AACR': 6},
        'by_phase': {'PHASE3': 18, 'PHASE2': 6},
        'high_probability': 14  # >= 75%
    }
}
```

## Parameters

- `quarter`: "Q1", "Q2", "Q3", "Q4"
- `year`: 2025, 2026, etc.
- `min_probability`: Minimum prediction probability (default: 0.6 = 60%)
- `companies`: Optional list of company names to filter
- `phases`: Optional trial phases to include (default: ["PHASE2", "PHASE3"])

## Probability Scoring

**Factors that increase probability:**

1. **Timing (50% weight)**:
   - Optimal window (3-9 months): +40-50%
   - Abstract deadline alignment: +10%

2. **Trial Phase (20% weight)**:
   - Phase 3: +20%
   - Phase 2: +15%
   - Phase 1: +10%

3. **Therapeutic Area Match (20% weight)**:
   - Primary conference: +20%
   - Secondary conference: +10%

4. **Trial Status (10% weight)**:
   - Completed (not terminated): +10%
   - Has results posted: +5%

**Probability Tiers:**
- **High (75-100%)**: Strong prediction - optimal timing + primary conference
- **Medium (60-74%)**: Likely - acceptable timing or secondary conference
- **Low (< 60%)**: Filtered out by default

## Integration with Discovery

After bottom-up discovery finds ~308 companies:
1. Run Trial Completion Predictor on all companies
2. Get predicted presentations for target quarter
3. Add to catalyst calendar as "PREDICTED" catalysts (estimated dates)
4. Cross-reference with Abstract Acceptance Tracker (confirmed vs predicted)

## Predicted vs Confirmed Catalysts

**Predicted (this skill)**:
- Based on trial completion + timing windows
- ~60-85% probability
- No SEC filing required
- Allows 2-4 month lead time

**Confirmed (Abstract Acceptance Tracker)**:
- Based on SEC 8-K abstract acceptance filing
- 100% confirmed (exact dates known)
- 4-8 week lead time

**Strategy**: Use predictions for early positioning, confirmations for final timing.

## Conference Timing Assumptions

Q4 2025 Conferences:
- **CTAD**: October 29 - November 1, 2025
- **ASH**: December 7-10, 2025

Q1 2026 Conferences:
- **ACC**: March 16-18, 2026

Q2 2026 Conferences:
- **AACR**: April 5-10, 2026
- **ASCO**: June 2-6, 2026
- **ADA**: June 23-27, 2026

Q3 2026 Conferences:
- **ESMO**: September 8-12, 2026

## Limitations

1. **Probabilistic**: Predictions, not confirmations (60-85% accuracy)
2. **Timing assumptions**: Companies may delay presentations for strategic reasons
3. **Conference selection**: Companies may choose secondary conferences
4. **Data availability**: Depends on trial completion data in ClinicalTrials.gov
5. **Abstract acceptance**: Companies may submit but not be accepted

## Validation

Compare predictions against Abstract Acceptance Tracker:
- Predicted + Confirmed = High confidence
- Predicted + Not confirmed = Lower priority
- Confirmed + Not predicted = Unexpected opportunity

---

**Category**: Catalyst Tracking
**Servers**: ct_gov_mcp
**Patterns**: Trial completion filtering, Conference matching, Probability scoring
**Complexity**: Medium (trial filtering + algorithmic scoring)
**Estimated Runtime**: 1-2 minutes (query trials + scoring)