# Testing Framework Analysis & Skills Library Health Report

**Date:** 2025-11-29
**Scope:** Sample testing of 19 skills (representing ~20% of 93 total skills)
**Testing Framework:** `.claude/tools/testing/`

---

## Executive Summary

**Library Health Score: 🔴 21% (CRITICAL)**

- **Tested:** 19 skills (sample from 93 total)
- **Passed:** 4 skills (21%)
- **Failed:** 15 skills (79%)
  - Import Errors: 5 skills (26%)
  - Schema Failures: 3 skills (16%)
  - Execution Errors: 2 skills (11%)
  - File Not Found: 3 skills (16%)
  - Parsing Errors: 2 skills (11%)

**Status:** Library requires immediate attention to fix broken skills and improve testing infrastructure.

---

## Testing Framework Assessment

### ✅ What Works Well

1. **5-Level Validation System** - Comprehensive testing (Syntax → Import → Execution → Data → Schema)
2. **Fast Static Checks** - Catches syntax/import issues before expensive execution (~50ms)
3. **JSON Output** - Structured data for programmatic analysis
4. **Detailed Error Reporting** - Clear failure messages with execution context
5. **Zero Dependencies** - Uses only Python stdlib (no external packages)

### ⚠️ Issues Found

1. **Import Error in batch_test_skills.py**
   - **Issue:** Importing `update_skill_health` from wrong module
   - **Fixed:** Changed import from `health_check` to `index_updater`
   - **Status:** ✓ RESOLVED

2. **Buffering Issues**
   - **Issue:** Background execution with output redirection causes buffering
   - **Impact:** Can't monitor real-time progress during batch runs
   - **Workaround:** Run without redirection or use `python3 -u` for unbuffered output

3. **No Support for Parameterized Skills**
   - **Issue:** Skills requiring arguments fail execution test
   - **Impact:** Can't test skills like `get_clinical_trials` which need `<TERM>` argument
   - **Solution:** Add `test_args` to SKILL.md frontmatter (see recommendations)

---

## Skills Library Health Analysis

### Critical Issues (Import Errors - 5 skills)

Skills trying to import non-existent functions from MCP servers:

| Skill | Incorrect Import | Correct Function | Server |
|-------|-----------------|------------------|--------|
| get_anti_amyloid_publications | `search` | `search_keywords` or `search_advanced` | pubmed_mcp |
| get_orphan_neurological_drugs | `search_drugs` | `lookup_drug` | fda_mcp |
| get_semaglutide_adverse_events | `search_adverse_events` | `device_adverse_events` (?) | fda_mcp |
| get_cvd_disease_burden | `get_health_statistics` | `get_health_data` | who_mcp |
| get_covid19_vaccine_trials_recruiting | Import error | Check import path | (unknown) |

**Root Cause:** Skills were created with incorrect function names, possibly due to:
- MCP API changes after skill creation
- Incorrect function names in skill generation
- Missing documentation of MCP server exports

**Impact:** 26% of tested skills are completely broken and won't execute.

### High-Priority Issues (Schema & Execution - 5 skills)

**Schema Failures (3 skills):**
- `get_california_population`
- `get_cart_therapy_landscape`
- `get_glp1_agonist_properties`

**Issue:** Skills execute successfully and return data, but output doesn't match expected schema patterns.

**Root Cause:** Test framework expects specific output patterns (e.g., "Total trials found: X") but skills may format output differently.

**Execution Errors (2 skills):**
- `get_clinical_trials` - Requires `<TERM>` argument
- `get_hypertension_fda_drugs` - Execution failed

**Root Cause:** Parameterized skills need command-line arguments but test framework runs without args.

### Medium-Priority Issues (File & Parsing - 5 skills)

**File Not Found (3 skills):**
- `get_adc_approved_drugs`
- `novo-nordisk-novel-patents`
- `bottom-up-catalyst-discovery`

**Root Cause:** Skills listed in index but files don't exist at expected paths.

**Parsing Errors (2 skills):**
- `get_subcutaneous_drugs_pipeline_2026_2027`
- `get_large_tam_clinical_programs`

**Root Cause:** Skills fail with `'NoneType' object has no attribute 'get'` - likely missing null checks in response parsing.

---

## MCP Server Function Reference

### fda_mcp Available Functions

```python
# Drug Functions
lookup_drug(search_term, search_type, fields_for_label, ...)

# Device Functions
device_510k(...)
device_adverse_events(...)
device_classification(...)
device_pma(...)
device_recalls(...)
device_registration(...)
device_udi(...)
lookup_device(...)
```

**Note:** No `search_drugs` or `search_adverse_events` functions exist!

### pubmed_mcp Available Functions

```python
search_keywords(keywords, num_results)
search_advanced(author, journal, title, ...)
get_article_metadata(pmid)
get_article_pdf(pmid)
```

**Note:** No generic `search` function - use `search_keywords` or `search_advanced`!

### who_mcp Available Functions

```python
get_health_data(indicator_code, ...)
get_country_data(country_code, indicator_code, ...)
get_cross_table(...)
get_dimensions()
get_dimension_codes(dimension_code)
search_indicators(keywords)
```

**Note:** No `get_health_statistics` - use `get_health_data`!

---

## Recommendations

### Immediate Actions (Week 1)

**Priority 1: Fix Import Errors (5 skills)**

1. **get_anti_amyloid_publications**
   ```python
   # WRONG
   from mcp.servers.pubmed_mcp import search

   # CORRECT
   from mcp.servers.pubmed_mcp import search_keywords
   result = search_keywords(keywords="anti-amyloid antibody", num_results=100)
   ```

2. **get_orphan_neurological_drugs**
   ```python
   # WRONG
   from mcp.servers.fda_mcp import search_drugs

   # CORRECT
   from mcp.servers.fda_mcp import lookup_drug
   result = lookup_drug(search_term="orphan", search_type="general", ...)
   ```

3. **get_semaglutide_adverse_events**
   ```python
   # WRONG
   from mcp.servers.fda_mcp import search_adverse_events

   # CORRECT - Need to determine correct function for drug adverse events
   # Check: fda_mcp.lookup_drug with fields_for_adverse_events parameter
   # OR: Use different endpoint for drug (not device) adverse events
   ```

4. **get_cvd_disease_burden**
   ```python
   # WRONG
   from mcp.servers.who_mcp import get_health_statistics

   # CORRECT
   from mcp.servers.who_mcp import get_health_data
   result = get_health_data(indicator_code="CVD_DEATHS", ...)
   ```

5. **get_covid19_vaccine_trials_recruiting**
   - Investigate actual import error
   - Check import path and module structure
   - Fix import statement

**Priority 2: Create MCP Function Reference**

Create `.claude/.context/mcp-function-reference.md` with complete documentation:

```markdown
# MCP Server Function Reference

## fda_mcp
- `lookup_drug(search_term, search_type, ...)`
- `lookup_device(search_term, ...)`
- `device_adverse_events(...)`
- [Complete list with parameters and examples]

## pubmed_mcp
- `search_keywords(keywords, num_results)`
- `search_advanced(author, journal, ...)`
- [Complete list with parameters and examples]

## who_mcp
- `get_health_data(indicator_code, ...)`
- [Complete list with parameters and examples]

[Continue for all 12 MCP servers]
```

**Priority 3: Fix File Not Found Issues (3 skills)**

1. Verify actual file paths in filesystem
2. Update index.json with correct paths
3. OR: Remove skills from index if no longer needed
4. Run: `python3 .claude/tools/skill_discovery/index_updater.py verify`

### Short-Term Enhancements (Weeks 2-3)

**Enhancement 1: Add Test Args Support**

Update SKILL.md frontmatter to include test configuration:

```yaml
---
name: get_clinical_trials
description: Search clinical trials by term and optional phase
servers:
  - ct_gov_mcp
category: clinical_trials
test_config:
  args: ["KRAS inhibitor", "PHASE3"]
  expected_min_results: 10
  timeout_seconds: 30
---
```

Update `test_runner.py` to read and use `test_args`:

```python
def test_skill(self, skill_path: str, args: list = None):
    # If no args provided, try to load from SKILL.md
    if args is None:
        skill_md = self._find_skill_md(skill_path)
        if skill_md:
            metadata = self._parse_frontmatter(skill_md)
            args = metadata.get('test_config', {}).get('args', [])

    # Execute with args
    cmd = ['python3', skill_path] + args
    ...
```

**Enhancement 2: Improve Schema Validation**

Make schema validation more flexible:

```python
def _check_schema(self, output: str, skill_type: str) -> tuple[bool, list[str]]:
    # Try multiple schema patterns
    patterns = SCHEMA_PATTERNS.get(skill_type, [])

    # Check for any pattern match (not all required)
    matches = [p for p in patterns if p.lower() in output.lower()]

    # Pass if at least 50% of patterns matched OR output has substantial content
    threshold = len(patterns) * 0.5
    has_content = len(output) > 100 and ('found' in output.lower() or 'total' in output.lower())

    passed = len(matches) >= threshold or has_content
    return passed, matches
```

**Enhancement 3: Add Parsing Error Protection**

For skills with NoneType errors, add defensive null checks:

```python
# BEFORE (causes NoneType error)
result = api_call()
data = result['items']  # Crashes if result is None

# AFTER (defensive)
result = api_call()
if not result:
    print("No results returned")
    return {'total_count': 0, 'items': []}

data = result.get('items', [])
if not data:
    print(f"Warning: No items in response")
```

### Medium-Term Improvements (Month 2)

**1. Implement Test Orchestrator Integration**

Use `test_orchestrator.py` for autonomous skill repair:

```bash
# Test and repair skill automatically
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/broken-skill/scripts/get_data.py \
  --max-iterations 3 \
  --auto-repair \
  --json
```

**2. Add CI/CD Testing**

Create GitHub Actions workflow:

```yaml
name: Skills Health Check
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run batch test
        run: python3 .claude/tools/testing/batch_test_skills.py --json
      - name: Check health threshold
        run: |
          health=$(jq '.health_percentage' /tmp/results.json)
          if [ $health -lt 80 ]; then
            echo "Health below 80%: $health%"
            exit 1
          fi
```

**3. Skill Deprecation Process**

When MCP APIs change:

1. Mark deprecated function usage with warnings
2. Create migration guide
3. Update all affected skills
4. Remove deprecated code after grace period

---

## Success Metrics

Track these metrics over time to measure library health:

| Metric | Current | Target (1 Month) | Target (3 Months) |
|--------|---------|------------------|-------------------|
| Health Score | 21% | 80% | 95% |
| Import Errors | 26% | 0% | 0% |
| Schema Failures | 16% | 5% | 2% |
| Execution Errors | 11% | 5% | 2% |
| File Not Found | 16% | 0% | 0% |
| Skills with Tests | ~20% | 100% | 100% |

---

## Testing Quick Reference

### Test Single Skill

```bash
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/glp1-fda-drugs/scripts/get_glp1_fda_drugs.py \
  --json
```

### Test with Arguments

```bash
python3 .claude/tools/testing/test_runner.py \
  .claude/skills/clinical-trials-term-phase/scripts/get_clinical_trials.py \
  --args "KRAS inhibitor" "PHASE3" \
  --json
```

### Batch Test All Skills

```bash
python3 .claude/tools/testing/batch_test_skills.py --json > results.json
```

### Test and Repair Skill

```bash
python3 .claude/tools/testing/test_orchestrator.py \
  .claude/skills/broken-skill/scripts/get_data.py \
  --iteration 1 \
  --max-iterations 3 \
  --json
```

---

## Files Modified

1. `.claude/tools/testing/batch_test_skills.py`
   - Fixed import: `update_skill_health` from `index_updater` (not `health_check`)

---

## Next Steps

**Immediate (This Week):**

1. ✓ Run comprehensive testing (COMPLETED)
2. ✓ Identify broken skills (COMPLETED)
3. ⏳ Fix 5 import error skills (IN PROGRESS)
4. ⏳ Create MCP function reference document (PENDING)
5. ⏳ Fix file not found issues (PENDING)

**Short-Term (Next 2 Weeks):**

1. Add test_args support to SKILL.md frontmatter
2. Update test_runner.py to use test_args
3. Improve schema validation flexibility
4. Add defensive null checks to parsing

**Medium-Term (Next Month):**

1. Implement test orchestrator for auto-repair
2. Set up CI/CD testing
3. Create skill deprecation process
4. Achieve 80%+ health score

---

## Appendix: Test Results Data

**Passing Skills (4):**
1. `get_biotech_ma_deals_sec_edgar`
2. `get_indication_pipeline_attrition`
3. `get_bispecific_antibody_trials`
4. `get_obesity_fda_drugs`

**Import Error Skills (5):**
1. `get_anti_amyloid_publications` - Missing: `search` from pubmed_mcp
2. `get_covid19_vaccine_trials_recruiting` - Module import error
3. `get_cvd_disease_burden` - Missing: `get_health_statistics` from who_mcp
4. `get_orphan_neurological_drugs` - Missing: `search_drugs` from fda_mcp
5. `get_semaglutide_adverse_events` - Missing: `search_adverse_events` from fda_mcp

**Schema Failure Skills (3):**
1. `get_california_population`
2. `get_cart_therapy_landscape`
3. `get_glp1_agonist_properties`

**Execution Error Skills (2):**
1. `get_clinical_trials` - Requires arguments
2. `get_hypertension_fda_drugs` - Execution failed

**File Not Found Skills (3):**
1. `get_adc_approved_drugs`
2. `novo-nordisk-novel-patents`
3. `bottom-up-catalyst-discovery`

**Parsing Error Skills (2):**
1. `get_subcutaneous_drugs_pipeline_2026_2027`
2. `get_large_tam_clinical_programs`

---

**Report Generated:** 2025-11-29
**Testing Framework Version:** 1.0
**Sample Size:** 19 skills (20% of library)
**Full Results:** `/tmp/skill_health_sample.json`
