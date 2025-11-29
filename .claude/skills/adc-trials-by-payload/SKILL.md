---
name: get_adc_trials_by_payload
description: >
  Analyzes ADC (antibody drug conjugate) clinical trials by payload class with comprehensive
  geographic and competitive intelligence. Built-in taxonomy covers topoisomerase I inhibitors
  (deruxtecan, exatecan), DNA-damaging agents (PBD, duocarmycin), and tubulin inhibitors
  (MMAE, MMAF, maytansine). Provides geographic distribution (US/EU vs China), target breakdown
  (HER2, TROP2, B7-H3, etc.), phase distribution, and sponsor competitive analysis.

  Strategic use cases:
  - Validate hypothesis: China prefers topoisomerase I payloads
  - Competitive intelligence: Which payload classes are most pursued?
  - Geographic patterns: Payload preferences by region
  - White space analysis: Under-explored payload-target combinations
  - Sponsor landscape: Who's leading in each payload class?

  Keywords: ADC, antibody drug conjugate, payload, topoisomerase, deruxtecan, MMAE, PBD,
  geographic analysis, China, competitive intelligence, target analysis, HER2, TROP2
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - geographic_classification
  - target_extraction
  - deduplication
data_scope:
  total_results: ~500-800 trials (varies by payload)
  geographical: Global
  temporal: All time
created: 2025-11-28
last_updated: 2025-11-28
complexity: complex
execution_time: ~30-60 seconds per payload class
token_efficiency: ~99% reduction vs raw data
---
# get_adc_trials_by_payload


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist Compare ADC trials by payload type - which payloads are most pursued?`
2. `@agent-pharma-search-specialist Do Chinese companies prefer topoisomerase I inhibitor ADCs versus Western companies?`
3. `@agent-pharma-search-specialist Show me the target-payload combinations in ADC clinical development`
4. `@agent-pharma-search-specialist What's the competitive landscape for MMAE-based ADCs?`
5. `@agent-pharma-search-specialist Which ADC payload classes are in late-stage development?`


## Purpose

Analyzes ADC (antibody drug conjugate) clinical trials segmented by payload class chemistry to identify geographic patterns, competitive landscape, and strategic opportunities in the ADC therapeutics space.

## Usage

**Parameterized by payload type**:
```python
# All ADCs (baseline)
result = get_adc_trials_by_payload('all')

# Topoisomerase I inhibitors (Daiichi Sankyo derivatives)
result = get_adc_trials_by_payload('topoisomerase_i')

# DNA-damaging agents (PBD, duocarmycin)
result = get_adc_trials_by_payload('dna_damaging')

# Tubulin inhibitors (MMAE, MMAF legacy)
result = get_adc_trials_by_payload('tubulin_inhibitor')
```

**When to use this skill**:
- Competitive intelligence queries about ADC payload preferences
- Geographic analysis of ADC development (US/EU vs China patterns)
- Target-payload combination analysis (which targets use which payloads?)
- White space identification in payload-target matrix
- Sponsor competitive positioning by payload class

## Implementation Details

### Payload Taxonomy

Built-in classification system:

```python
payload_classes = {
    'topoisomerase_i': {
        'search_terms': ['deruxtecan', 'DXd', 'SN-38', 'exatecan',
                        'topoisomerase I inhibitor'],
        'description': 'Topoisomerase I inhibitor payloads'
    },
    'dna_damaging': {
        'search_terms': ['PBD', 'pyrrolobenzodiazepine', 'duocarmycin',
                        'calicheamicin'],
        'description': 'DNA-damaging agent payloads'
    },
    'tubulin_inhibitor': {
        'search_terms': ['MMAE', 'MMAF', 'monomethyl auristatin',
                        'maytansine', 'DM1', 'DM4'],
        'description': 'Tubulin inhibitor payloads'
    },
    'all': {
        'search_terms': ['antibody drug conjugate', 'ADC'],
        'description': 'All ADC trials (baseline)'
    }
}
```

### Geographic Classification

Heuristic-based classification using sponsor names and trial locations:

- **China**: Chinese company names, Beijing, Shanghai, Guangzhou, etc.
- **US/EU**: Major Western pharma (Pfizer, Merck, Roche, etc.)
- **Other**: Neither clear China nor US/EU indicators

### Target Extraction

Regex-based extraction of 15+ common ADC targets:
- HER2, TROP2, B7-H3, NECTIN-4
- CD19, CD22, CD30, CD33, CD79B
- EGFR, MUC16, FOLR1, GPRC5D, BCMA, CEACAM5

### Data Collection

- **Pagination**: 1000-record pages with pageToken continuation
- **Deduplication**: NCT ID tracking across search terms
- **Multiple searches**: Aggregates across all payload-specific search terms
- **Markdown parsing**: CT.gov trial extraction and field parsing

## Output Structure

```python
{
    'total_trials': int,
    'payload_type': str,  # 'all', 'topoisomerase_i', etc.
    'payload_description': str,
    'geographic_distribution': {
        'US_EU': count,
        'China': count,
        'Other': count
    },
    'target_breakdown': {
        'HER2': count,
        'TROP2': count,
        # ... all detected targets
    },
    'phase_distribution': {
        'PHASE1': count,
        'PHASE2': count,
        'PHASE3': count,
        'PHASE4': count
    },
    'top_sponsors': [
        {
            'name': str,
            'count': int,
            'geography': str  # 'US_EU', 'China', or 'Other'
        },
        # ... top 10 sponsors
    ],
    'summary': str  # Text summary with key insights
}
```

## Strategic Insights Enabled

1. **Geography-Payload Correlation**: Validate if China prefers topoisomerase I payloads vs Western preference for tubulin inhibitors
2. **Competitive Positioning**: Identify leaders in each payload class by sponsor and geography
3. **Target-Payload Matrix**: Discover which targets are being pursued with which payloads
4. **White Space Analysis**: Find under-explored payload-target combinations
5. **Market Timing**: Phase distribution indicates maturity of each payload class

## Example Queries Answered

- "Do Chinese companies prefer topoisomerase I inhibitor ADCs?" → Compare geographic distribution across payload types
- "Which targets are most pursued with MMAE payloads?" → Run tubulin_inhibitor type, analyze target breakdown
- "Who are the top sponsors in DNA-damaging ADCs?" → Run dna_damaging type, review top_sponsors
- "What's the total ADC landscape?" → Run 'all' type for baseline

## Verification

Skill includes:
- ✅ Pagination (complete dataset collection)
- ✅ Deduplication (NCT ID tracking)
- ✅ Executable standalone (if __name__ == "__main__")
- ✅ Valid schema (all required fields present)
- ✅ Error handling (try-except on MCP calls)

## Dependencies

- `mcp.servers.ct_gov_mcp` - ClinicalTrials.gov search
- Python standard library: `re`, `collections.defaultdict`

## Performance

- **Execution time**: ~30-60 seconds per payload class (multiple searches with pagination)
- **Token efficiency**: ~99% (only summary enters context, full dataset stays in execution)
- **Data volume**: ~500-800 total ADC trials, varies by payload class

## Related Skills

- `get_enhanced_antibody_trials_by_geography` - Reference pattern for geographic classification
- `get_glp1_trials` - Reference pattern for pagination and deduplication