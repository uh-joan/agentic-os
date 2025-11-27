# Skill Discovery & CLI Interface Issues - Analysis & Fixes

**Date:** 2025-11-27
**Triggered by:** Semaglutide SWOT analysis execution

---

## Issue 1: Strategy Tool Doesn't Support Strategic Analysis Skills

### What Happened

```bash
python3 .claude/tools/skill_discovery/strategy.py \
  --skill "generate_drug_swot_analysis" \
  --data-type "strategic_analysis"  # ❌ INVALID

Error: argument --data-type: invalid choice: 'strategic_analysis'
(choose from trials, fda_drugs, patents, publications)
```

### Root Cause

**File:** `.claude/tools/skill_discovery/strategy.py:215`

```python
parser.add_argument('--data-type', required=True,
    choices=['trials', 'fda_drugs', 'patents', 'publications'])  # ❌ Too restrictive
```

**Design Limitation:**
- Strategy tool designed for simple data collection skills only
- Hardcoded choices exclude strategic/composite skills
- SWOT analysis uses 4 MCP servers (ct_gov, fda, pubmed, uspto_patents) - doesn't fit single data type

**Skills Affected:**
- `generate_drug_swot_analysis` (strategic-analysis category)
- `get_rare_disease_acquisition_targets` (strategic-analysis category)
- `analyze_company_product_launch_timeline` (regulatory category, complex)
- `get_ra_targets_and_trials` (target-validation, multi-server)
- Any future strategic/composite skills

### Why This Is a Problem

1. **Can't discover strategic skills via strategy tool**
   - Forces manual index lookups
   - No intelligent REUSE/ADAPT/CREATE decision

2. **Inconsistent workflow**
   - Simple skills: Use strategy.py
   - Complex skills: Manual process

3. **Future scalability issue**
   - As we build more strategic agents, this becomes a bigger bottleneck

### Fix Options

#### Option A: Extend Strategy Tool (Recommended)

**Changes to `.claude/tools/skill_discovery/strategy.py`:**

```python
# Line 215 - Expand choices
parser.add_argument('--data-type', required=True,
    choices=[
        'trials',
        'fda_drugs',
        'patents',
        'publications',
        'strategic_analysis',      # NEW: Multi-server composite
        'financial_analysis',      # NEW: SEC/Yahoo Finance
        'competitive_intelligence', # NEW: Multi-dimensional
        'target_validation'        # NEW: OpenTargets + CT.gov
    ])

# Line 74-80 - Update reference selection logic
def find_best_reference(requirements: SkillRequirements) -> dict:
    """Find best skill to use as reference for creating new skill."""
    # ... existing code ...

    if requirements.data_type == 'trials':
        pattern_cat = pattern_categories.get('ct_gov_queries', {})
    elif requirements.data_type == 'fda_drugs':
        pattern_cat = pattern_categories.get('fda_queries', {})
    elif requirements.data_type == 'strategic_analysis':
        pattern_cat = pattern_categories.get('multi_server_query', {})  # NEW
    elif requirements.data_type == 'financial_analysis':
        pattern_cat = pattern_categories.get('sec_xbrl_parsing', {})   # NEW
    # ... etc ...
```

**Update `.claude/skills/index.json` pattern_categories:**

```json
"pattern_categories": {
  "multi_server_query": {
    "description": "Patterns for strategic analysis combining multiple MCP servers",
    "best_reference": "generate_drug_swot_analysis",
    "skills": ["generate_drug_swot_analysis", "get_ra_targets_and_trials"]
  },
  "strategic_analysis": {
    "description": "Composite skills for strategic decision-making",
    "best_reference": "generate_drug_swot_analysis",
    "skills": ["generate_drug_swot_analysis", "get_rare_disease_acquisition_targets"]
  }
}
```

**Benefits:**
- ✅ Unified workflow for all skill types
- ✅ Intelligent REUSE/ADAPT/CREATE for strategic skills
- ✅ Maintains existing functionality
- ✅ Future-proof for new categories

**Effort:** Low (30 minutes)

#### Option B: Direct Index Query for Known Skills (Quick Fix)

**Workflow:**
1. Check if skill name exists in index.json
2. If found and healthy → Execute directly
3. If not found → Fall back to strategy tool OR pharma-search-specialist

**Implementation:**

```python
# New utility: .claude/tools/skill_discovery/quick_lookup.py
def find_skill_by_name(skill_name: str) -> Optional[dict]:
    """Quick lookup by exact skill name."""
    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    for skill in index['skills']:
        if skill['name'] == skill_name:
            return skill
    return None

# Usage in main agent
skill = find_skill_by_name('generate_drug_swot_analysis')
if skill and skill.get('health', {}).get('status') == 'healthy':
    # Execute directly - no strategy needed
    Bash(f"python3 {skill['script']} {args}")
else:
    # Fall back to strategy or creation
```

**Benefits:**
- ✅ Extremely fast (no strategy overhead)
- ✅ Works today with zero changes
- ✅ Simple to understand

**Drawbacks:**
- ⚠️ No ADAPT logic (can't learn from similar skills)
- ⚠️ Requires exact name match

**Effort:** Trivial (5 minutes)

#### Option C: Hybrid Approach (Best of Both)

1. **First:** Quick index lookup by name
2. **If not found:** Use extended strategy tool
3. **If strategy fails:** Invoke pharma-search-specialist

**Decision Tree:**
```
User requests skill
    ↓
Quick lookup in index.json
    ↓
Found + healthy? → Execute immediately
    ↓
Not found? → Strategy tool (extended)
    ↓
Strategy = REUSE? → Execute
Strategy = ADAPT? → Modify and execute
Strategy = CREATE? → Invoke pharma-search-specialist
```

**Benefits:**
- ✅ Fast path for known skills
- ✅ Intelligent discovery for new skills
- ✅ Graceful degradation

**Effort:** Medium (1 hour)

---

## Issue 2: Inconsistent CLI Argument Formats

### What Happened

**First attempt (assumed argparse):**
```bash
python3 generate_drug_swot_analysis.py --drug-name "semaglutide" --indication "diabetes"
# ❌ Failed - skill uses positional arguments
```

**Correct usage (positional):**
```bash
python3 generate_drug_swot_analysis.py semaglutide diabetes
# ✅ Success
```

### Root Cause

**Inconsistent CLI patterns across skills:**

| Skill | CLI Pattern | Example |
|-------|-------------|---------|
| `generate_drug_swot_analysis` | Positional (`sys.argv`) | `python skill.py semaglutide diabetes` |
| `get_companies_by_moa` | Positional (`sys.argv`) | `python skill.py "GLP-1" diabetes` |
| `company_clinical_trials_portfolio` | Named (`argparse`) | `python skill.py --sponsor-name Pfizer` |
| `company_pipeline_indications` | Named (`argparse`) | `python skill.py --company "Novo Nordisk"` |
| `get_rare_disease_acquisition_targets` | Named (`argparse`) | `python skill.py --therapeutic-focus ultra_rare` |

**Why This Happened:**
- Skills created at different times with different conventions
- No CLI standardization guideline
- `index.json` shows `cli_enabled: true` but doesn't specify argument format

### Why This Is a Problem

1. **Unpredictable execution**
   - Can't determine CLI format without reading source code
   - Trial-and-error required

2. **Poor user experience**
   - Named arguments are self-documenting (`--drug-name semaglutide`)
   - Positional arguments require memorization (`semaglutide diabetes` - which is which?)

3. **No help system**
   - Most skills lack `--help` flag
   - Error messages don't show proper usage

### Fix Options

#### Option A: Standardize on argparse (Recommended)

**Standard Template:**

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate SWOT analysis for pharmaceutical product',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generate_drug_swot_analysis.py --drug-name semaglutide --indication diabetes
  python generate_drug_swot_analysis.py --drug-name "Keytruda" --indication "lung cancer"
        '''
    )
    parser.add_argument('--drug-name', required=True, help='Generic or brand name')
    parser.add_argument('--indication', required=True, help='Therapeutic area')

    args = parser.parse_args()

    result = generate_drug_swot_analysis(args.drug_name, args.indication)
    # ... print results ...
```

**Migration Plan:**
1. Update all `cli_enabled: true` skills to use argparse
2. Keep positional as positional (no `--` prefix) for backward compatibility option
3. Add `--help` to all CLI skills

**Skills to update (18 total):**
- ✅ Already using argparse: 6 skills
- ❌ Need migration: 12 skills (including drug-swot-analysis)

**Effort:** Medium (2-3 hours for all 12 skills)

#### Option B: Document CLI Format in Index

**Update `index.json` to include CLI signature:**

```json
{
  "name": "generate_drug_swot_analysis",
  "cli_enabled": true,
  "cli_format": "positional",  // NEW
  "cli_signature": "<drug_name> <indication>",  // NEW
  "cli_example": "semaglutide diabetes"  // NEW
}
```

**Agent can then:**
1. Read `cli_format` and `cli_signature` from index
2. Construct correct command automatically
3. Show example to user on error

**Benefits:**
- ✅ No code changes to skills
- ✅ Immediate solution
- ✅ Self-documenting

**Drawbacks:**
- ⚠️ Doesn't improve user experience (positional still unclear)
- ⚠️ Maintenance burden (keep index and code in sync)

**Effort:** Low (1 hour to update all index entries)

#### Option C: Hybrid - Document Now, Migrate Later

1. **Phase 1 (This week):** Add CLI metadata to index.json
2. **Phase 2 (Next sprint):** Migrate all skills to argparse
3. **Phase 3 (Future):** Remove legacy positional support

**Benefits:**
- ✅ Immediate improvement via documentation
- ✅ Long-term standardization
- ✅ Gradual migration (low risk)

**Effort:** Low now, medium later

---

## Recommended Implementation Plan

### Week 1: Quick Wins
1. **Add Option B (Index Documentation)** - 1 hour
   - Update `index.json` with CLI metadata for all 18 CLI-enabled skills
   - Agent can now construct correct commands

2. **Implement Option B from Issue 1 (Quick Lookup)** - 30 min
   - Add `find_skill_by_name()` utility
   - Fast path for exact skill name matches

### Week 2: Strategic Improvements
3. **Extend Strategy Tool (Option A, Issue 1)** - 1 hour
   - Add `strategic_analysis`, `financial_analysis` data types
   - Update reference selection logic
   - Add pattern categories to index

4. **Migrate Priority Skills to argparse (Option A, Issue 2)** - 2 hours
   - Start with most-used: drug-swot-analysis, companies-by-moa
   - Create standard template
   - Add `--help` flag

### Week 3: Complete Migration
5. **Migrate Remaining Skills** - 2 hours
   - Update all 12 positional-argument skills
   - Test each migration
   - Update documentation

### Total Effort: ~6.5 hours over 3 weeks

---

## Success Metrics

**Before Fixes:**
- ❌ 2 execution failures on simple SWOT request
- ❌ No way to discover strategic skills via strategy tool
- ❌ Trial-and-error required for CLI usage

**After Fixes:**
- ✅ Zero failures - correct execution on first attempt
- ✅ All skills discoverable via unified workflow
- ✅ Self-documenting CLI with `--help` on all skills
- ✅ Index metadata enables intelligent command construction

---

## Long-Term Vision

### CLI Standardization Guidelines

**For all future skills:**

1. **Use argparse for all CLI interfaces**
   - Named arguments (`--argument-name`)
   - Required arguments marked with `required=True`
   - Optional arguments with sensible defaults

2. **Include help text**
   - Description of what skill does
   - Examples section with 2-3 use cases
   - All arguments documented

3. **Update index.json with CLI metadata**
   - `cli_enabled: true`
   - `cli_signature: "--drug-name <name> --indication <indication>"`
   - `cli_example: "--drug-name semaglutide --indication diabetes"`

4. **Test CLI before merging**
   - Run with `--help`
   - Test with example from documentation
   - Verify error messages are helpful

### Skill Discovery Best Practices

**For agents invoking skills:**

1. **Try quick lookup first**
   ```python
   skill = find_skill_by_name(exact_name)
   if skill and healthy: execute()
   ```

2. **Fall back to strategy tool**
   ```python
   else: strategy = determine_skill_strategy(name, requirements)
   ```

3. **Use CLI metadata from index**
   ```python
   cmd = f"python3 {skill['script']} {format_args(skill['cli_signature'], args)}"
   ```

---

## Implementation Tracker

- [ ] Document CLI metadata in index.json (18 skills)
- [ ] Add `find_skill_by_name()` utility
- [ ] Extend strategy.py with strategic_analysis type
- [ ] Add pattern_categories for strategic skills
- [ ] Migrate drug-swot-analysis to argparse
- [ ] Migrate companies-by-moa to argparse
- [ ] Migrate remaining 10 skills to argparse
- [ ] Update CLAUDE.md with CLI standards
- [ ] Create skill creation template with argparse
- [ ] Test all migrations

---

**Next Steps:** Start with Week 1 quick wins (2 hours total effort, immediate impact).
