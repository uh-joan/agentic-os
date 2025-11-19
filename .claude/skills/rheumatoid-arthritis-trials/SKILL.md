---
name: get_rheumatoid_arthritis_trials
description: >
  Retrieves comprehensive data on all rheumatoid arthritis clinical trials from ClinicalTrials.gov.
  Uses pagination to collect complete dataset (7648 trials as of 2025-11-19).
  Essential for competitive intelligence in autoimmune disease space, pipeline analysis, and strategic
  planning for RA therapeutics including JAK inhibitors, TNF inhibitors, and novel mechanisms.
  Trigger keywords: rheumatoid arthritis, RA trials, autoimmune trials, JAK inhibitor, TNF inhibitor,
  biologic DMARD, methotrexate combination, baricitinib, upadacitinib, filgotinib, adalimumab.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - complete_dataset_collection
data_scope:
  total_results: 7648
  geographical: Global
  temporal: All time (inception to current)
created: 2025-11-19
last_updated: 2025-11-19
complexity: medium
execution_time: ~12 seconds
token_efficiency: ~99% reduction vs raw markdown data
---

# get_rheumatoid_arthritis_trials

## Purpose
Collects complete dataset of rheumatoid arthritis clinical trials from ClinicalTrials.gov using pagination to handle large result sets (7648 trials).

## Usage
Use this skill when you need:
- Complete RA pipeline visibility across all phases
- Competitive landscape analysis in autoimmune/rheumatology space
- JAK inhibitor vs biologic DMARD market dynamics
- Clinical development trends and patterns (e.g., combination therapies)
- Strategic planning for RA programs
- Benchmark data for trial design in autoimmune diseases

## Implementation Details

### Data Source
- **Server**: `ct_gov_mcp` (ClinicalTrials.gov API)
- **Search Term**: "rheumatoid arthritis"
- **Response Format**: Markdown string (not JSON)
- **Page Size**: 1000 trials per page
- **Pagination**: Token-based (handles 7648 total trials)

### Key Features
1. **Complete Data Collection**: Pagination loop retrieves all 7648 trials (not limited to first 1000)
2. **Progress Tracking**: Real-time feedback on pages fetched and trials collected
3. **Efficient Parsing**: Regex patterns extract trial sections from markdown
4. **Summary Format**: Returns total count + first 10 trials as sample

### Proven Patterns Applied
- **Pagination Logic**: Follows same pattern as `get_glp1_trials.py` (battle-tested on 1803 trials)
- **Token Extraction**: `Next page token: (\S+)` regex to get pagination token
- **Trial Parsing**: `## Study: (.*?)\n(.*?)` regex to extract trial sections
- **Error Handling**: Breaks loop when no more trials found

### Technical Notes
- **CT.gov Specificity**: Only CT.gov returns markdown - all other MCP servers return JSON
- **Token Efficiency**: ~99% reduction (150k+ tokens → ~2k summary tokens)
- **Execution Time**: ~12 seconds for 7648 trials (8 API calls with 1000 records each)

## Example Output

```
Rheumatoid Arthritis Clinical Trials

Total trials found: 7648

Sample Trials (First 10):
- Baricitinib (JAK inhibitor) vs Adalimumab (TNF inhibitor)
- Filgotinib (JAK inhibitor) + Methotrexate combinations
- Tocilizumab (IL-6 inhibitor) vs Anti-TNF comparisons
- Upadacitinib (JAK inhibitor) in DMARD-IR populations
- Novel biosimilars (BCD-055 vs Humira)
...
```

## Related Skills
- `get_glp1_trials` - Similar pagination pattern (CT.gov trials)
- `get_kras_inhibitor_trials` - Similar markdown parsing (CT.gov trials)
- `get_adc_trials` - Similar large dataset handling (CT.gov trials)

## Future Enhancements
- Add phase filtering (e.g., only Phase 3 trials)
- Add status filtering (e.g., only recruiting trials)
- Add sponsor/drug filtering for competitive intelligence
- Add temporal analysis (trials by year)
- Add geographical breakdown (US vs EU vs Asia trials)
