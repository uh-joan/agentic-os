# get_braf_inhibitor_trials

Get BRAF inhibitor clinical trials across all phases from ClinicalTrials.gov.

## Usage

### As importable function
```python
from .claude.skills.get_braf_inhibitor_trials import get_braf_inhibitor_trials

result = get_braf_inhibitor_trials()
print(f"Total trials: {result['total_count']}")
print(result['trials_summary'])
```

### As executable script
```bash
cd /path/to/agentic-os
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_braf_inhibitor_trials.py
```

## Returns

Dictionary with:
- `total_count` (int): Total number of BRAF inhibitor trials found
- `trials_summary` (str): Markdown-formatted summary of all trials

## Features

- ✅ **Complete data retrieval**: Handles pagination to get ALL trials (not limited to first 1000)
- ✅ **Proven pagination pattern**: Reuses battle-tested implementation from get_glp1_trials.py
- ✅ **Dual-mode**: Both importable and executable
- ✅ **ClinicalTrials.gov**: Official NIH trials registry

## Data Source

- **MCP Server**: `ct_gov_mcp`
- **API**: ClinicalTrials.gov search
- **Search Term**: "BRAF inhibitor"
- **Response Format**: Markdown string (unique to CT.gov server)

## Implementation Notes

**Pagination Pattern** (from get_glp1_trials.py):
1. Initial request with pageSize=1000
2. Extract total count from markdown response
3. Extract pageToken if present
4. Loop: Fetch next page → Extract token → Continue until all results retrieved
5. Combine all pages with separator: "\n\n---\n\n"

**Why This Matters**:
- CT.gov API limits single response to 1000 trials
- BRAF inhibitors have 729 trials (< 1000, but pattern handles growth)
- Pattern ensures complete dataset even if trials increase beyond 1000

## Example Output

```
Total BRAF inhibitor trials found: 729

Trials summary:
Total trials found: 729

## Trial: Dabrafenib and Trametinib in Treating Patients With BRAF Mutation...
- **NCT ID**: NCT02034110
- **Status**: Completed
- **Phase**: Phase 2
- **Conditions**: Melanoma
...
[729 trials with full details]
```

## Pattern Reuse

This skill demonstrates:
- ✅ **Pattern Discovery**: Found get_glp1_trials.py via ls .claude/skills/get_*_trials.py
- ✅ **Pattern Application**: Reused proven pagination logic (lines 15-64 from reference)
- ✅ **Consistency**: Same structure, same conventions, same quality
- ✅ **Completeness**: Guaranteed to retrieve all trials regardless of count

## Related Skills

- `get_glp1_trials.py` - Reference implementation with pagination
- `get_adc_trials.py` - ADC trials with same pattern
- `get_kras_inhibitor_trials.py` - KRAS trials with same pattern

## Metadata

- **Created**: 2025-01-19
- **Pattern Source**: get_glp1_trials.py (pagination pattern)
- **MCP Server**: ct_gov_mcp
- **Response Format**: Markdown (CT.gov unique)
- **Pagination**: Yes (proven pattern)
- **Total Results**: 729 trials (as of 2025-01-19)
