# Source Attribution Migration Guide

## Overview

This guide documents the standardized pattern for migrating existing skills to include source attribution metadata. This migration is part of Phase 3 of the Source Attribution implementation plan.

## Migration Status

**Phase 3 Progress:**
- **Completed:** 5 sample skills migrated and verified across 5 MCP servers
- **Remaining:** 98 skills need migration (~97% of total skills library)
- **Pattern Established:** Standardized 6-step migration pattern validated

## Sample Skills Migrated

| Skill | MCP Server | Verification | Notes |
|-------|------------|--------------|-------|
| `glp1-fda-drugs` | `fda_mcp` | ✅ PASSED | FDA JSON response |
| `diabetes-recruiting-trials` | `ct_gov_mcp` | ✅ PASSED | CT.gov with pagination |
| `anti-amyloid-antibody-publications` | `pubmed_mcp` | ✅ PASSED | PubMed with temporal chunking |
| `company-rd-spending` | `sec_edgar_mcp` | ✅ PASSED (warning) | SEC EDGAR financial data |
| `alzheimers-therapeutic-targets` | `opentargets_mcp` | ✅ PASSED | Open Targets genetic data |

## Standardized Migration Pattern

### Step 1: Add datetime Import

Add `datetime` import if not already present:

```python
import sys
sys.path.insert(0, ".claude")
from datetime import datetime  # ADD THIS LINE
from mcp.servers.ct_gov_mcp import search
```

### Step 2: Disable Print Statements

Comment out all `print()` statements to ensure clean JSON output:

```python
# Before:
print(f"Fetching data for {ticker}...")

# After:
# print(f"Fetching data for {ticker}...")  # Disabled for JSON output
```

**Critical:** All debug/status print statements must be disabled for JSON verification to work.

### Step 3: Wrap Return Data

Wrap existing return data in a `'data'` key:

```python
# Before:
return {
    'drugs': unique_drugs,
    'total_count': len(unique_drugs)
}

# After:
return {
    'data': {
        'drugs': unique_drugs,
        'total_count': len(unique_drugs)
    },
    'source_metadata': {
        # ... (added in next step)
    },
    'summary': "..."
}
```

### Step 4: Add Source Metadata

Add complete `source_metadata` section with all 6 required fields:

```python
'source_metadata': {
    'source': 'ClinicalTrials.gov',           # Human-readable source name
    'mcp_server': 'ct_gov_mcp',               # MCP server identifier
    'query_date': datetime.now().strftime('%Y-%m-%d'),  # ISO 8601 date
    'query_params': {                          # Original query parameters
        'query': 'diabetes',
        'recruitmentStatus': 'RECRUITING',
        'pageSize': 1000
    },
    'data_count': len(all_trials),            # Number of records returned
    'data_type': 'clinical_trials'            # Type of data (trials/drugs/publications/etc)
}
```

### Step 5: Update Summary with Source Citation

Add source citation to the summary string:

```python
'summary': f"Found {total_count} trials (source: ClinicalTrials.gov, {datetime.now().strftime('%Y-%m-%d')})"
```

### Step 6: Update Executable Block

Replace human-readable output with JSON output:

```python
# Before:
if __name__ == "__main__":
    result = get_skill_function()
    print(f"Total: {result['total_count']}")
    print(result['summary'])

# After:
if __name__ == "__main__":
    import json
    result = get_skill_function()

    # For JSON verification (required by verify_source_attribution.py)
    print(json.dumps(result, indent=2))
```

### Step 7: Handle Error Returns

Apply the same pattern to ALL error return statements:

```python
# Before:
if not data:
    return {'error': 'No data found'}

# After:
if not data:
    return {
        'data': {},
        'source_metadata': {
            'source': 'ClinicalTrials.gov',
            'mcp_server': 'ct_gov_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {...},
            'data_count': 0,
            'data_type': 'clinical_trials'
        },
        'summary': f"No data found (source: ClinicalTrials.gov, {datetime.now().strftime('%Y-%m-%d')})",
        'error': 'No data found'
    }
```

## MCP Server-Specific Patterns

### FDA (fda_mcp)
- **Source Name:** `"FDA Drug Database"`
- **Data Types:** `fda_approved_drugs`, `adverse_events`, `recalls`
- **Response Format:** JSON dict
- **Query Params:** Typically `{'search_terms': [...], 'search_type': 'general', 'limit': 100}`

### ClinicalTrials.gov (ct_gov_mcp)
- **Source Name:** `"ClinicalTrials.gov"`
- **Data Types:** `clinical_trials`
- **Response Format:** Markdown string (requires parsing)
- **Query Params:** `{'query': '...', 'recruitmentStatus': '...', 'pageSize': 1000}`
- **Special:** May include pagination (`pageToken`)

### PubMed (pubmed_mcp)
- **Source Name:** `"PubMed"`
- **Data Types:** `publications`, `literature`
- **Response Format:** JSON dict
- **Query Params:** `{'keywords': '...', 'num_results': 100}` or temporal chunking
- **Special:** Complex skills may use temporal chunking strategy

### SEC EDGAR (sec_edgar_mcp)
- **Source Name:** `"SEC EDGAR"`
- **Data Types:** `financial_data`, `company_facts`
- **Response Format:** JSON dict
- **Query Params:** `{'ticker': '...', 'quarters': 8, 'cik_or_ticker': '...'}`

### Open Targets (opentargets_mcp)
- **Source Name:** `"Open Targets Platform"`
- **Data Types:** `therapeutic_targets`, `genetic_associations`, `disease_targets`
- **Response Format:** JSON dict
- **Query Params:** `{'disease_query': '...', 'min_score': 0.0, 'max_targets': 50}`

### WHO (who_mcp)
- **Source Name:** `"World Health Organization (WHO)"`
- **Data Types:** `health_statistics`, `disease_burden`
- **Response Format:** JSON dict

### CDC (cdc_mcp)
- **Source Name:** `"Centers for Disease Control and Prevention (CDC)"`
- **Data Types:** `disease_surveillance`, `health_indicators`
- **Response Format:** JSON dict

### Data Commons (datacommons_mcp)
- **Source Name:** `"Data Commons"`
- **Data Types:** `population_statistics`, `demographic_data`
- **Response Format:** JSON dict

### PubChem (pubchem_mcp)
- **Source Name:** `"PubChem"`
- **Data Types:** `compound_properties`, `chemical_data`
- **Response Format:** JSON dict

### USPTO Patents (uspto_patents_mcp)
- **Source Name:** `"United States Patent and Trademark Office (USPTO)"`
- **Data Types:** `patents`, `patent_applications`
- **Response Format:** JSON dict
- **Note:** Per user instruction, skip migrating patent skills for now

### Healthcare (healthcare_mcp)
- **Source Name:** `"Centers for Medicare & Medicaid Services (CMS)"`
- **Data Types:** `cms_provider_data`, `medicare_claims`
- **Response Format:** JSON dict

### Financials (financials_mcp)
- **Source Name:** `"Yahoo Finance"` or `"Federal Reserve Economic Data (FRED)"`
- **Data Types:** `stock_data`, `economic_indicators`
- **Response Format:** JSON dict

### NLM Codes (nlm_codes_mcp)
- **Source Name:** `"National Library of Medicine (NLM)"`
- **Data Types:** `icd_codes`, `medical_codes`
- **Response Format:** JSON dict

## Verification Process

After migrating each skill, verify it:

```bash
# Test execution
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/{skill-folder}/scripts/{skill-name}.py 2>&1 > /tmp/output.json

# Verify source attribution
python3 .claude/tools/verification/verify_source_attribution.py \
  --type skill \
  --execution-output "$(cat /tmp/output.json)" \
  --json
```

**Expected result:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "recommendations": []
}
```

**Acceptable warnings:**
- MCP server name format warnings (e.g., `sec_edgar_mcp` vs `sec_mcp`)

**Unacceptable errors:**
- Missing source_metadata fields
- Invalid JSON output
- Missing data wrapper

## Common Pitfalls

### 1. Print Statements Not Disabled
**Problem:** Verification fails with "Invalid JSON" error
**Cause:** Print statements mixing with JSON output
**Solution:** Comment out ALL print() calls, search for `print(` in file

### 2. Missing Error Return Updates
**Problem:** Some code paths don't have source_metadata
**Cause:** Forgot to update error return statements
**Solution:** Search for ALL `return {` statements and update each

### 3. Incorrect Date Format
**Problem:** Verification fails on query_date field
**Cause:** Using wrong date format or timezone
**Solution:** Always use `datetime.now().strftime('%Y-%m-%d')` (ISO 8601)

### 4. Missing Datetime Import
**Problem:** NameError: name 'datetime' is not defined
**Cause:** Forgot to add datetime import
**Solution:** Add `from datetime import datetime` at top of file

### 5. Wrong Data Count
**Problem:** data_count doesn't match actual records
**Cause:** Using wrong variable or counting method
**Solution:** Use `len(results)` or `total_count` variable consistently

### 6. Inconsistent MCP Server Names
**Problem:** Verification warnings about server name
**Cause:** Using `sec_edgar_mcp` instead of `sec_mcp` (verification tool naming)
**Solution:** Use full server name from skill imports (e.g., `sec_edgar_mcp`)

## Migration Checklist

For each skill:

- [ ] Step 1: Add `from datetime import datetime` import
- [ ] Step 2: Comment out all `print()` statements
- [ ] Step 3: Wrap existing return data in `'data'` key
- [ ] Step 4: Add `'source_metadata'` with all 6 required fields
- [ ] Step 5: Update `'summary'` with source citation
- [ ] Step 6: Update `if __name__ == "__main__":` block for JSON output
- [ ] Step 7: Update ALL error return statements with same pattern
- [ ] Test: Run skill and check for clean JSON output
- [ ] Verify: Run verification tool and confirm PASS
- [ ] Document: Note any warnings or special cases

## Batch Migration Strategy

For migrating remaining 98 skills:

### Phase 1: Analyze (Already Complete)
- ✅ Run migration helper to analyze all skills
- ✅ Group by MCP server type
- ✅ Identify reference patterns

### Phase 2: Prioritize Servers
Migrate in this order:
1. **CT.gov (highest usage)** - ~25 skills
2. **FDA** - ~15 skills
3. **PubMed** - ~12 skills
4. **SEC EDGAR** - ~10 skills
5. **Open Targets** - ~8 skills
6. **WHO/CDC** - ~10 skills
7. **Other servers** - ~18 skills
8. **Skip: USPTO patents** - per user instruction

### Phase 3: Batch Migration
For each server group:
1. Select 1 representative skill as reference
2. Apply pattern to all skills in group
3. Run batch verification
4. Fix any failures
5. Commit changes with descriptive message

### Phase 4: Documentation Update
- Update `.claude/CLAUDE.md` to reflect source attribution requirement
- Update `skill-frontmatter-template.yaml` with source_metadata example
- Update agent prompts to require source attribution in new skills

## Automation Opportunities

### Semi-Automated Migration Script
A Python script could automate most steps:
1. Parse skill file
2. Detect MCP server imports
3. Insert datetime import
4. Comment out print statements
5. Wrap return statements
6. Generate source_metadata template
7. Update executable block
8. Run verification
9. Report results

**Status:** Not yet implemented
**Effort:** ~4 hours to develop and test
**Benefit:** ~80% reduction in manual migration time

## References

- **Implementation Plan:** `.claude/.context/implementation-plans/source-attribution-implementation-plan.md`
- **Verification Tool:** `.claude/tools/verification/verify_source_attribution.py`
- **Migration Helper:** `.claude/tools/migrate_skills_source_metadata.py`
- **MCP Server Mapping:** See `SOURCE_NAME_MAPPING` in migration helper

## Migration Progress Tracking

Track progress using git commits:

```bash
# Per-skill commits
git commit -m "Migrate {skill-name} to source attribution pattern ({server})"

# Batch commits
git commit -m "Migrate {n} CT.gov skills to source attribution pattern"
```

Use branch for migration work:
```bash
git checkout -b feature/source-attribution-migration
# ... migrate skills ...
git push origin feature/source-attribution-migration
```

## Next Steps

1. **Immediate:** Begin batch migration of CT.gov skills (~25 skills)
2. **Week 1:** Complete FDA, PubMed, SEC EDGAR migrations (~37 skills)
3. **Week 2:** Complete Open Targets, WHO/CDC, other servers (~36 skills)
4. **Week 3:** Update documentation and agent prompts
5. **Week 4:** Implement semi-automated migration script for future use

**Total Estimated Effort:** 3-4 weeks at ~10 skills per day

## Success Criteria

Migration is complete when:
- ✅ All non-patent skills have source_metadata (103 skills)
- ✅ All skills pass verification with no errors
- ✅ Documentation updated to reflect source attribution requirement
- ✅ Agents configured to require source attribution in new skills
- ✅ Migration patterns documented for future maintenance

---

*Document created: 2025-12-03*
*Last updated: 2025-12-03*
*Status: Phase 3 Sample Migration Complete (5/103 skills)*
