---
name: get_rheumatoid_arthritis_fda_drugs
description: >
  Retrieves FDA-approved drugs for rheumatoid arthritis from FDA drug labels database.
  Returns comprehensive list with drug names (brand and generic), manufacturers,
  approval dates, and indications. Includes biologics (TNF inhibitors, IL-6 inhibitors),
  JAK inhibitors, and traditional DMARDs. Automatically deduplicates results and sorts
  alphabetically. Use when analyzing RA treatment landscape, competitive intelligence,
  or regulatory approval timelines. Triggers: "rheumatoid arthritis drugs", "RA FDA approved",
  "rheumatoid arthritis treatments", "RA biologics", "JAK inhibitors RA".
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - deduplication
  - data_extraction
data_scope:
  total_results: 41
  geographical: US (FDA approved)
  temporal: All approved drugs (historical to current)
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw FDA data
---

# get_rheumatoid_arthritis_fda_drugs

## Purpose
Retrieves all FDA-approved drugs for rheumatoid arthritis treatment from the FDA drug labels database. Provides comprehensive information including brand names, generic names, manufacturers, approval dates, and indications.

## Usage
Use this skill when you need to:
- Analyze the rheumatoid arthritis treatment landscape
- Compare FDA-approved RA therapies
- Research competitor drugs for RA
- Track approval timelines for RA treatments
- Identify biologics, JAK inhibitors, and DMARDs for RA

## Trigger Keywords
- "rheumatoid arthritis drugs"
- "RA FDA approved"
- "rheumatoid arthritis treatments"
- "RA biologics"
- "JAK inhibitors RA"
- "TNF inhibitors RA"
- "DMARDs FDA"

## Implementation Details

### Data Source
- **MCP Server**: `fda_mcp`
- **API Function**: `search_drug_labels`
- **Search Term**: "rheumatoid arthritis"
- **Response Format**: JSON

### Processing Logic
1. Query FDA drug labels database with search term "rheumatoid arthritis"
2. Extract drug information from OpenFDA fields:
   - Brand name (primary) or generic name (fallback)
   - Manufacturer name
   - Application number (for approval date extraction)
   - Indications and usage
3. Deduplicate results by drug name (case-insensitive)
4. Sort alphabetically by drug name
5. Format summary with key details

### Key Features
- **Deduplication**: Removes duplicate entries by drug name
- **Comprehensive data**: Brand name, generic name, manufacturer, approval date, indications
- **Smart fallback**: Uses generic name if brand name unavailable
- **Date extraction**: Attempts to extract approval year from application numbers
- **Sorted output**: Alphabetical ordering for easy reference

### Return Format
```python
{
    'total_count': int,  # Number of unique drugs found
    'drugs': [
        {
            'drug_name': str,        # Brand or generic name
            'manufacturer': str,      # Company name
            'approval_date': str,     # Year of approval or 'Unknown'
            'indications': str,       # First 200 chars of indication text
            'generic_name': str       # Generic name or 'N/A'
        },
        ...
    ],
    'summary': str  # Formatted text summary
}
```

## Example Output
```
Total drugs found: 41

• ACTEMRA (tocilizumab)
  Manufacturer: Genentech, Inc.
  Approval: 2010
  Indication: ACTEMRA is indicated for treatment of adult patients with...

• CIMZIA (certolizumab pegol)
  Manufacturer: UCB Manufacturing, Inc.
  Approval: 2008
  Indication: CIMZIA is a tumor necrosis factor (TNF) blocker indicated for...

• ENBREL (etanercept)
  Manufacturer: Immunex Corporation
  Approval: 1998
  Indication: Reducing signs and symptoms, inducing major clinical response...
```

## Data Scope
- **Total results**: 41 FDA-approved drugs
- **Therapeutic classes**: Biologics (TNF inhibitors, IL-6 inhibitors), JAK inhibitors, DMARDs
- **Geographical scope**: US (FDA approved only)
- **Temporal scope**: All historically approved drugs (1990s to present)

## Performance
- **Execution time**: ~2 seconds
- **Token efficiency**: ~99% reduction (raw FDA data never enters context)
- **API limit**: 100 results per query (sufficient for RA drugs)

## Related Skills
- `get_rheumatoid_arthritis_trials` - Clinical trials for RA (CT.gov)
- `get_tnf_inhibitor_fda_drugs` - Specific TNF inhibitor drugs
- `get_jak_inhibitor_fda_drugs` - JAK inhibitors across indications

## Notes
- FDA drug labels database is the authoritative source for approved drugs
- Approval dates extracted from application numbers may not always be precise
- Results include both brand names and generic equivalents
- Some drugs may have multiple FDA-approved indications beyond RA
