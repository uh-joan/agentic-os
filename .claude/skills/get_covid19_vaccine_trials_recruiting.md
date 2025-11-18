# get_covid19_vaccine_trials_recruiting

**Category**: Clinical Trials Research
**MCP Server**: ct_gov_mcp
**Created**: 2025-01-18

## Purpose

Query ClinicalTrials.gov for active COVID-19 vaccine trials currently recruiting globally. Provides comprehensive analysis of the active global research landscape including phase distribution, sponsor diversity, and geographic reach.

## Function Signature

```python
def get_covid19_vaccine_trials_recruiting() -> dict
```

## Returns

```python
{
    'total_trials': int,           # Total number of recruiting trials
    'trials': [                     # List of trial dictionaries
        {
            'nct_id': str,          # NCT Number
            'title': str,           # Trial title
            'status': str,          # Recruitment status
            'phase': str,           # Trial phase
            'sponsor': str,         # Lead sponsor
            'countries': str,       # Participating countries
            'study_type': str,      # Study type
            'enrollment': str       # Target enrollment
        }
    ],
    'phase_distribution': dict,     # Count of trials by phase
    'top_sponsors': dict,           # Top 10 sponsors and trial counts
    'countries_count': int,         # Number of unique countries
    'unique_countries': list        # Sorted list of countries
}
```

## MCP Tool Used

- `ct_gov_studies`
  - **condition**: "COVID-19"
  - **intervention**: "vaccine"
  - **status**: "RECRUITING"
  - **fields**: NCTId, BriefTitle, OverallStatus, Phase, LeadSponsorName, LocationCountry, StudyType, EnrollmentCount

## Usage Example

```python
from .claude.skills.get_covid19_vaccine_trials_recruiting import get_covid19_vaccine_trials_recruiting

# Get current COVID-19 vaccine trial landscape
results = get_covid19_vaccine_trials_recruiting()

print(f"Total recruiting trials: {results['total_trials']}")
print(f"Phase 3 trials: {results['phase_distribution'].get('Phase 3', 0)}")
print(f"Countries involved: {results['countries_count']}")

# Access individual trial details
for trial in results['trials'][:5]:
    print(f"{trial['nct_id']}: {trial['title']}")
    print(f"  Sponsor: {trial['sponsor']}")
    print(f"  Phase: {trial['phase']}")
```

## Key Insights (Example Results)

- **73 trials** actively recruiting globally
- **49 countries** participating
- **All phases represented**: Phase 1 (18), Phase 2 (14), Phase 3 (13), combined phases, and Phase 4
- **Diverse sponsors**: Academic institutions, government agencies, pharmaceutical companies
- **Global distribution**: Strong presence in US, China, Europe, Latin America, Asia

## Pattern Demonstrated

- ✅ CT.gov markdown response parsing
- ✅ Multi-field data extraction from markdown
- ✅ Statistical aggregation (phases, sponsors, countries)
- ✅ Handling variable-length lists (countries)
- ✅ Top-N filtering (top 10 sponsors)
- ✅ Data normalization and counting

## Dependencies

- `mcp.servers.ct_gov_mcp.ct_gov_studies`
- Standard library: `sys`, `re`, `pathlib`

## Related Skills

- `get_phase2_alzheimers_trials_us.py` - Disease-specific trial search
- `get_us_phase3_obesity_recruiting_trials.py` - Phase-specific trial search
- Future: `compare_vaccine_trials_by_disease.py` - Cross-disease comparison

## Notes

- CT.gov returns **markdown string**, not JSON
- Response parsed using line-by-line field label matching
- Countries are comma-separated strings requiring split and deduplication
- Phase distribution useful for understanding development stage distribution
- Geographic reach indicates trial accessibility across regions
