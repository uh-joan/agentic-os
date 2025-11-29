# Skill Deprecation Strategy

## Overview

When generalizing a disease-specific skill into a reusable generic skill, follow this deprecation strategy to maintain backward compatibility while guiding users toward the improved version.

## Example: diabetes-drugs-stopped-safety → safety-stopped-trials

### What We Did

#### 1. Created Generic Skill
- **New skill**: `.claude/skills/safety-stopped-trials/`
- **Parameterized**: Works for any therapeutic area
- **Preserved logic**: All 90% of original code reused
- **Enhanced flexibility**: Optional condition_subtypes parameter

#### 2. Deprecated Legacy Skill (3-Step Process)

**Step 1: Update SKILL.md Frontmatter**
```yaml
---
name: get_diabetes_drugs_stopped_safety
deprecated: true                              # Mark as deprecated
deprecated_date: 2025-11-28                   # Document when
replacement: safety-stopped-trials            # Point to new skill folder
replacement_skill: get_safety_stopped_trials  # Point to new function
migration_guide: |                            # Provide migration instructions
  Use the generic safety-stopped-trials skill instead:
  - Old: get_diabetes_drugs_stopped_safety()
  - New: get_safety_stopped_trials("diabetes", condition_subtypes={...})
---
```

**Step 2: Add Deprecation Notice to Documentation**
```markdown
# get_diabetes_drugs_stopped_safety

> **⚠️ DEPRECATED (2025-11-28)**
>
> This skill has been superseded by the generic **`safety-stopped-trials`** skill.
>
> **Migration:**
> ```python
> # Old (diabetes-specific)
> result = get_diabetes_drugs_stopped_safety()
>
> # New (generic, recommended)
> result = get_safety_stopped_trials("diabetes", condition_subtypes={...})
> ```
```

**Step 3: Convert Script to Thin Wrapper**

Reduced from **541 lines** to **85 lines**:

```python
"""
⚠️ DEPRECATED WRAPPER (2025-11-28)
This skill has been superseded by the generic 'safety-stopped-trials' skill.
"""

import sys
import warnings
import os
import importlib.util

# Import the generic skill
spec = importlib.util.spec_from_file_location(
    "get_safety_stopped_trials",
    os.path.join(os.path.dirname(__file__), "../../safety-stopped-trials/scripts/get_safety_stopped_trials.py")
)
safety_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety_module)
get_safety_stopped_trials = safety_module.get_safety_stopped_trials


def get_diabetes_drugs_stopped_safety():
    """DEPRECATED: Wraps the generic safety-stopped-trials skill."""

    # Emit deprecation warning
    warnings.warn(
        "get_diabetes_drugs_stopped_safety() is deprecated. "
        "Use get_safety_stopped_trials('diabetes', ...) instead.",
        DeprecationWarning,
        stacklevel=2
    )

    # Call generic skill with diabetes-specific parameters
    return get_safety_stopped_trials(
        indication="diabetes",
        condition_subtypes={
            'Type 1 Diabetes': ['type 1', 'type i', 't1d'],
            'Type 2 Diabetes': ['type 2', 'type ii', 't2d'],
            'Gestational Diabetes': ['gestational', 'gdm']
        }
    )


if __name__ == "__main__":
    print("=" * 80)
    print("⚠️  DEPRECATION NOTICE")
    print("=" * 80)
    print("This skill is deprecated as of 2025-11-28.")
    print("Replacement: safety-stopped-trials (generic, works for any indication)")
    print("=" * 80)

    result = get_diabetes_drugs_stopped_safety()
    print("\n" + result['summary'])
```

## Benefits of This Approach

### ✅ Backward Compatibility
- **Existing code continues to work** - No breaking changes
- **Same API** - Function signature unchanged
- **Same results** - Wrapper delegates to generic version

### ✅ Clear Migration Path
- **Visible warnings** - DeprecationWarning + CLI notice
- **Documentation** - Migration guide in SKILL.md
- **Code examples** - Old vs New side-by-side

### ✅ Reduced Maintenance
- **Single source of truth** - Generic skill contains all logic
- **Bug fixes propagate** - Fix once in generic, wrapper inherits
- **No code duplication** - Wrapper is 85 lines vs 541 lines

### ✅ Discoverable
- **Frontmatter flags** - `deprecated: true` enables automated detection
- **Replacement pointer** - `replacement_skill` guides users
- **Date tracking** - `deprecated_date` for lifecycle management

## Verification

The wrapper was tested and confirmed working:

```bash
$ python get_diabetes_drugs_stopped_safety.py

================================================================================
⚠️  DEPRECATION NOTICE
================================================================================
This skill (diabetes-drugs-stopped-safety) is deprecated as of 2025-11-28.
Replacement: safety-stopped-trials (generic, works for any indication)
Migration:
  Old: python get_diabetes_drugs_stopped_safety.py
  New: python get_safety_stopped_trials.py "diabetes"
================================================================================

# ... executes successfully and returns results ...
✓ Exit code: 0
✓ Python DeprecationWarning emitted
✓ Same 135 trials found
✓ Same results as generic version
```

## When to Use This Strategy

Use this deprecation strategy when:
- ✅ Generalizing disease-specific skill → generic skill
- ✅ Consolidating multiple similar skills → single parameterized skill
- ✅ Maintaining backward compatibility is important
- ✅ Users need clear migration path

Do NOT use for:
- ❌ Skills with broken/invalid logic (delete instead)
- ❌ Experimental/unverified skills (archive instead)
- ❌ Skills with zero usage (can delete)

## Alternative Strategies

### Option 1: Hard Deprecation (Delete)
- Remove skill entirely
- Risk: Breaking changes for existing users
- Use when: Skill is unused or fundamentally flawed

### Option 2: Archive
- Move to `.claude/skills/_archived/`
- Keep for historical reference only
- Risk: Breaks imports
- Use when: Skill is no longer relevant

### Option 3: Soft Deprecation (Wrapper) ⭐ **RECOMMENDED**
- Convert to thin wrapper
- Maintain backward compatibility
- Guide users to better option
- Use when: Skill has been generalized/improved

## Future Cleanup

After **6-12 months** of deprecation period:
1. Check usage metrics (if available)
2. If usage is negligible, consider hard deletion
3. Otherwise, keep wrapper indefinitely (it's only 85 lines)

## Skills Using This Pattern

| Legacy Skill | Generic Replacement | Deprecated Date | Status |
|--------------|---------------------|-----------------|--------|
| `diabetes-drugs-stopped-safety` | `safety-stopped-trials` | 2025-11-28 | ✅ Wrapper active |

---

**Last Updated**: 2025-11-28
**Pattern Established**: diabetes-drugs-stopped-safety deprecation
**Next Review**: 2026-06-28 (6 months)
