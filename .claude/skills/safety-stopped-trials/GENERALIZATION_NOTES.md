# Safety-Stopped-Trials Generalization

## Summary

Successfully generalized `diabetes-drugs-stopped-safety` skill into `safety-stopped-trials` - now works for any therapeutic area while preserving all sophisticated safety analysis logic.

## Key Changes

### 1. Function Signature (Parameterization)

**Before** (diabetes-specific):
```python
def get_diabetes_drugs_stopped_safety():
    """Get diabetes clinical trials stopped due to safety concerns."""
```

**After** (generic):
```python
def get_safety_stopped_trials(indication, condition_subtypes=None):
    """Get clinical trials stopped due to safety concerns for any indication.

    Args:
        indication (str): Disease/therapeutic area (e.g., "diabetes", "NSCLC", "obesity")
        condition_subtypes (dict, optional): Mapping for disease-specific categorization
    """
```

### 2. Query Construction (Line 47)

**Before** (hardcoded):
```python
query = f'diabetes AND (AREA[OverallStatus]TERMINATED OR ...) AND AREA[WhyStopped]{keyword}'
```

**After** (parameterized):
```python
query = f'{indication} AND (AREA[OverallStatus]TERMINATED OR ...) AND AREA[WhyStopped]{keyword}'
```

### 3. Condition Subtype Categorization (Lines 200-209)

**Before** (diabetes-specific, hardcoded):
```python
# Hardcoded diabetes subtypes
if 'type 1' in conditions_lower or 'type i' in conditions_lower or 't1d' in conditions_lower:
    dtype = 'Type 1 Diabetes'
elif 'type 2' in conditions_lower or 'type ii' in conditions_lower or 't2d' in conditions_lower:
    dtype = 'Type 2 Diabetes'
elif 'gestational' in conditions_lower or 'gdm' in conditions_lower:
    dtype = 'Gestational Diabetes'
else:
    dtype = 'Other/Unspecified'
```

**After** (generic, parameterized):
```python
# Optional parameter-driven subtypes
if condition_subtypes:
    # User provided subtype mappings - apply them
    subtype_found = False
    for subtype_label, keywords in condition_subtypes.items():
        if any(keyword in conditions_lower for keyword in keywords):
            categorizations['by_condition_subtype'][subtype_label] = ...
            subtype_found = True
            break
    if not subtype_found:
        categorizations['by_condition_subtype']['Other/Unspecified'] = ...
else:
    # No subtypes provided - categorize all as "Other/Unspecified"
    categorizations['by_condition_subtype']['Other/Unspecified'] = ...
```

### 4. Command-Line Interface

**Added** flexible CLI with JSON support:
```python
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_safety_stopped_trials.py <indication> [<condition_subtypes_json>]")
        sys.exit(1)

    indication = sys.argv[1]

    # Optional: Parse condition subtypes from JSON
    condition_subtypes = None
    if len(sys.argv) >= 3:
        condition_subtypes = json.loads(sys.argv[2])

    result = get_safety_stopped_trials(indication, condition_subtypes)
```

## What Stayed the Same (90% of Code)

All core safety analysis logic preserved:
- ✅ **Safety keyword scoring** (lines 26-33): 11 keywords with severity weights
- ✅ **Multi-keyword search** (lines 39-91): Union of trials across all keywords
- ✅ **Trial detail parsing** (lines 144-181): Extract "Why Stopped" text
- ✅ **Drug scoring algorithm** (lines 257-396): 4-dimensional scoring system
- ✅ **Phase/status categorization** (lines 184-233): Generic phase/status logic
- ✅ **Formatting/visualization** (lines 399-535): Tables, examples, summaries

## Usage Examples

### Example 1: Diabetes (with subtypes)

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/safety-stopped-trials/scripts/get_safety_stopped_trials.py "diabetes" '{"Type 1": ["type 1", "t1d"], "Type 2": ["type 2", "t2d"], "Gestational": ["gestational", "gdm"]}'
```

### Example 2: NSCLC (no subtypes)

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/safety-stopped-trials/scripts/get_safety_stopped_trials.py "NSCLC"
```

### Example 3: Cancer (with subtypes)

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/safety-stopped-trials/scripts/get_safety_stopped_trials.py "cancer" '{"Lung": ["nsclc", "small cell"], "Breast": ["triple negative", "her2+"], "Colorectal": ["colorectal", "crc"]}'
```

### Example 4: Python import

```python
from skills.safety_stopped_trials.scripts.get_safety_stopped_trials import get_safety_stopped_trials

# Basic usage (no subtypes)
result = get_safety_stopped_trials("obesity")
print(f"Total safety-stopped trials: {result['total_count']}")

# With subtypes
subtypes = {
    'EGFR+': ['egfr', 'egfr mutation', 'egfr+'],
    'KRAS+': ['kras', 'kras mutation', 'kras+'],
    'ALK+': ['alk', 'alk rearrangement', 'alk+']
}
result = get_safety_stopped_trials("NSCLC", condition_subtypes=subtypes)
```

## Verification

Tested with diabetes:
- ✅ Found 135 safety-stopped trials
- ✅ Categorized by status: Terminated (118), Withdrawn (13), Suspended (4)
- ✅ Categorized by phase: Phase 2 (39), Phase 3 (37), N/A (21), Phase 4 (14)
- ✅ Executed without errors (exit code 0)
- ✅ Same results as original diabetes-specific skill

## Backward Compatibility

The original `diabetes-drugs-stopped-safety` skill is preserved for backward compatibility. Users can:
1. **Migrate** to the generic skill for all future work
2. **Keep using** the diabetes-specific skill if already integrated
3. **Gradually transition** by testing the generic version first

Recommended: Use `safety-stopped-trials` for all new projects. The diabetes-specific skill may be deprecated in future versions.

## Benefits of Generalization

1. **Reusability**: Works for any therapeutic area (diabetes, NSCLC, obesity, etc.)
2. **Flexibility**: Optional condition subtypes for disease-specific categorization
3. **Consistency**: Same safety analysis logic across all indications
4. **Maintainability**: Single codebase instead of N disease-specific versions
5. **Discoverability**: Registered in skill index with clear metadata

## Files Created

- `.claude/skills/safety-stopped-trials/SKILL.md` - Documentation
- `.claude/skills/safety-stopped-trials/scripts/get_safety_stopped_trials.py` - Generic implementation
- `.claude/skills/safety-stopped-trials/GENERALIZATION_NOTES.md` - This file

## Index Registration

Skill registered in `.claude/skills/index.json`:
- Name: `get_safety_stopped_trials`
- Category: `safety-intelligence`
- Servers: `ct_gov_mcp`
- Patterns: `focused_query`, `safety_keyword_scoring`, `drug_failure_analysis`, `multi_keyword_search`
- Complexity: `moderate`

---

**Date**: 2025-11-28
**Created by**: Generalization of diabetes-drugs-stopped-safety
**Status**: ✅ Tested and verified
