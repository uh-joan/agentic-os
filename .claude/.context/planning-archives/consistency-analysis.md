# Documentation Consistency Analysis

**Date**: 2025-11-19
**Purpose**: Identify all inconsistencies after migration to folder structure

## Issues Found

### 1. Import Path References (CRITICAL)

**Problem**: All documentation still shows flat structure imports

**Locations**:
- `.claude/CLAUDE.md` - Line 364 (example import)
- `.claude/.context/code-examples/ctgov_markdown_parsing.md` - Line 80
- `.claude/.context/code-examples/fda_json_parsing.md` - Line 80
- `.claude/.context/code-examples/skills_library_pattern.md` - Lines 178, 263, 302, 303
- All 11 `SKILL.md` files in folder structure (usage examples)
- `.claude/skills/README.md` - Lines 63-64

**Current (WRONG)**:
```python
from .claude.skills.get_glp1_trials import get_glp1_trials
```

**Should be (CORRECT)**:
```python
from .claude.skills.glp1_trials.scripts.get_glp1_trials import get_glp1_trials
```

### 2. Execution Path References

**Problem**: Some docs show flat execution paths

**Current (WRONG)**:
```bash
python3 .claude/skills/get_glp1_trials.py
```

**Should be (CORRECT)**:
```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/glp1-trials/scripts/get_glp1_trials.py
```

### 3. SKILL.md Files Usage Section

**Problem**: All 11 SKILL.md files have outdated import examples

**Affected files**:
- `glp1-trials/SKILL.md`
- `glp1-fda-drugs/SKILL.md`
- `kras-inhibitor-trials/SKILL.md`
- `kras-inhibitor-fda-drugs/SKILL.md`
- `glp1-diabetes-drugs/SKILL.md`
- `covid19-vaccine-trials-recruiting/SKILL.md`
- `phase2-alzheimers-trials-us/SKILL.md`
- `us-phase3-obesity-recruiting-trials/SKILL.md`
- `adc-trials/SKILL.md`
- `braf-inhibitor-trials/SKILL.md`
- `braf-inhibitor-fda-drugs/SKILL.md`

### 4. Code Examples

**Problem**: Examples in `.claude/.context/code-examples/` show old patterns

**Files to update**:
- `ctgov_markdown_parsing.md` - Shows flat import
- `fda_json_parsing.md` - Shows flat import
- `skills_library_pattern.md` - Multiple references to flat structure

### 5. CLAUDE.md Architecture Section

**Problem**: Has outdated import example in "Skill File Standards" section

**Location**: Line 364

## Priority Fixes

### Priority 1: SKILL.md Files (User-Facing)
All 11 SKILL.md files need updated usage examples

### Priority 2: CLAUDE.md (Main Documentation)
Update architecture examples to show folder structure

### Priority 3: Code Examples (Agent Reference)
Update code-examples/ to reflect new pattern

### Priority 4: Skills README
Update .claude/skills/README.md with folder structure examples

## Recommended Changes

### Standard Import Pattern (NEW)
```python
# Folder structure import (v2.0)
from .claude.skills.{folder_name}.scripts.{function_name} import {function_name}

# Example: GLP-1 trials
from .claude.skills.glp1_trials.scripts.get_glp1_trials import get_glp1_trials
```

### Standard Execution Pattern (NEW)
```bash
# Folder structure execution (v2.0)
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/{folder-name}/scripts/{function_name}.py

# Example: GLP-1 trials
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/glp1-trials/scripts/get_glp1_trials.py
```

### Standard Usage Section Template (for SKILL.md)
```markdown
## Usage

### Import and Use
\```python
from .claude.skills.{folder_name}.scripts.{function_name} import {function_name}

result = {function_name}()
print(result)
\```

### Execute Directly
\```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/{folder-name}/scripts/{function_name}.py
\```
```

## Files Requiring Updates

1. `.claude/CLAUDE.md` (1 location)
2. `.claude/.context/code-examples/ctgov_markdown_parsing.md` (1 location)
3. `.claude/.context/code-examples/fda_json_parsing.md` (1 location)
4. `.claude/.context/code-examples/skills_library_pattern.md` (4 locations)
5. `.claude/skills/README.md` (2 locations)
6. All 11 SKILL.md files in folder structure (1 location each)

**Total**: 20 locations across 16 files

## Testing Strategy

After updates:
1. Verify all import examples are correct
2. Test actual skill execution
3. Verify agent can read and understand new patterns
4. Run real query to test end-to-end
