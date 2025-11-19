# Anthropic Skills Hybrid Approach - Migration Plan

## Overview

**Goal**: Adopt Anthropic's skill packaging conventions while preserving our code-execution strengths.

**Strategy**: Phased migration with testing at each phase. Both formats coexist during transition.

**Current State**:
- 11 skills in flat structure (.py + .md pairs)
- No YAML frontmatter
- Working code execution pattern
- Pattern discovery via index.json

**Target State**:
- Self-contained skill folders (skill-name/)
- YAML frontmatter with standardized metadata
- Code in scripts/ subdirectory
- Enhanced index.json
- Backward compatibility maintained

---

## Phase 1: Add YAML Frontmatter (Non-Breaking)

**Duration**: 2-3 hours
**Risk**: Low (additive only, no breaking changes)
**Rollback**: Simple (remove frontmatter)

### 1.1 Create YAML Frontmatter Template

**File**: `.claude/.context/templates/skill-frontmatter-template.yaml`

```yaml
---
name: {skill_name}
description: >
  {What this skill does and when to use it. Be specific about use cases.
  Include: data source, scope, special capabilities (pagination, etc.).
  Triggers: keywords that indicate this skill should be used.}
category: {clinical-trials|drug-discovery|financial|regulatory|target-validation}
mcp_servers:
  - {server_name}
patterns:
  - {pattern_name}
data_scope:
  total_results: {number}
  geographical: {US|Global|EU|etc}
  temporal: {All time|Recent|2020-2025|etc}
created: {YYYY-MM-DD}
last_updated: {YYYY-MM-DD}
complexity: {simple|medium|complex}
execution_time: {~N seconds}
token_efficiency: {N% reduction vs raw data}
---
```

**Test**: Validate YAML parses correctly
```bash
python3 -c "import yaml; yaml.safe_load(open('.claude/.context/templates/skill-frontmatter-template.yaml'))"
```

### 1.2 Add Frontmatter to Existing Skills

**Process for each skill**:

1. Read existing `.md` file
2. Extract metadata:
   - name: from filename
   - description: from ## Overview section
   - category: infer from content
   - mcp_servers: from ## Data Source section
   - patterns: from index.json entry
   - complexity: from index.json or infer from LOC
3. Generate YAML frontmatter
4. Prepend to existing markdown content
5. Preserve all existing documentation

**Order of migration** (start with reference skills):
1. ✅ `get_glp1_trials.md` - Complex, has pagination (best reference)
2. ✅ `get_glp1_fda_drugs.md` - Simple, JSON parsing
3. ✅ `get_kras_inhibitor_trials.md` - Simple variant
4. ✅ `get_kras_inhibitor_fda_drugs.md` - Simple variant
5. ✅ Remaining 7 skills

**Example transformation**:

**Before** (`get_glp1_trials.md`):
```markdown
# get_glp1_trials

## Overview
Collects comprehensive clinical trial data for GLP-1...
```

**After**:
```markdown
---
name: get_glp1_trials
description: >
  Collect comprehensive GLP-1 clinical trial data from ClinicalTrials.gov
  with full pagination support. Retrieves complete dataset of 1800+ trials
  across all phases, statuses, and geographic regions. Use when analyzing
  GLP-1 drug development pipeline, competitive landscape, or clinical trial
  activity. Handles large result sets automatically via pagination.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - status_aggregation
data_scope:
  total_results: 1803
  geographical: Global
  temporal: All time
created: 2025-11-19
last_updated: 2025-11-19
complexity: medium
execution_time: ~3-5 seconds
token_efficiency: 98.7% reduction vs raw data
---

# get_glp1_trials

## Overview
Collects comprehensive clinical trial data for GLP-1...
```

### 1.3 Update index.json with Frontmatter References

**File**: `.claude/skills/index.json`

Add `has_frontmatter: true` flag and frontmatter_path reference:

```json
{
  "version": "1.1",
  "format": "hybrid-transition",
  "skills": [
    {
      "name": "get_glp1_trials",
      "file": "get_glp1_trials.py",
      "documentation": "get_glp1_trials.md",
      "has_frontmatter": true,
      "structure": "flat",
      "description": "Get GLP-1 clinical trials with full pagination support...",
      ...
    }
  ]
}
```

### 1.4 Create Frontmatter Parser Utility

**File**: `.claude/scripts/parse_skill_metadata.py`

```python
#!/usr/bin/env python3
"""Parse YAML frontmatter from skill documentation files."""

import yaml
from pathlib import Path
from typing import Dict, Optional

def parse_skill_frontmatter(skill_md_path: Path) -> Optional[Dict]:
    """Extract YAML frontmatter from skill .md file.

    Args:
        skill_md_path: Path to skill .md file

    Returns:
        Dictionary of metadata, or None if no frontmatter
    """
    content = skill_md_path.read_text()

    # Check for frontmatter delimiters
    if not content.startswith('---\n'):
        return None

    # Extract frontmatter
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return None

    frontmatter_text = parts[1]

    try:
        metadata = yaml.safe_load(frontmatter_text)
        return metadata
    except yaml.YAMLError as e:
        print(f"Error parsing frontmatter in {skill_md_path}: {e}")
        return None

def get_all_skill_metadata() -> Dict[str, Dict]:
    """Get metadata for all skills with frontmatter.

    Returns:
        Dictionary mapping skill names to their metadata
    """
    skills_dir = Path('.claude/skills')
    skills = {}

    for md_file in skills_dir.glob('*.md'):
        if md_file.name == 'README.md':
            continue

        metadata = parse_skill_frontmatter(md_file)
        if metadata:
            skill_name = metadata.get('name', md_file.stem)
            skills[skill_name] = metadata

    return skills

if __name__ == "__main__":
    # Test utility
    skills = get_all_skill_metadata()
    print(f"Found {len(skills)} skills with frontmatter:")
    for name, meta in skills.items():
        print(f"  - {name}: {meta.get('category', 'unknown')} ({meta.get('complexity', 'unknown')})")
```

### 1.5 Phase 1 Testing

**Test Plan**:

1. **Validate YAML syntax**:
```bash
python3 .claude/scripts/parse_skill_metadata.py
# Should list all skills with parsed metadata
```

2. **Check backward compatibility**:
```bash
# Existing skills should still work (Python imports unchanged)
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_glp1_trials.py
```

3. **Test metadata extraction**:
```python
from pathlib import Path
import sys
sys.path.insert(0, '.claude/scripts')
from parse_skill_metadata import parse_skill_frontmatter

metadata = parse_skill_frontmatter(Path('.claude/skills/get_glp1_trials.md'))
assert metadata['name'] == 'get_glp1_trials'
assert 'ct_gov_mcp' in metadata['mcp_servers']
assert 'pagination' in metadata['patterns']
print("✓ Frontmatter parsing works")
```

4. **Test agent can read frontmatter**:
   - Agent invokes skill
   - Agent reads .md file
   - Agent accesses description from frontmatter
   - Agent uses metadata for skill selection

**Success Criteria**:
- ✅ All 11 skills have valid YAML frontmatter
- ✅ All skills still executable (no breaking changes)
- ✅ Parser utility works correctly
- ✅ index.json updated with frontmatter flags
- ✅ No user-facing changes (skills work exactly as before)

**Rollback Procedure**:
```bash
# Remove frontmatter from all .md files
for file in .claude/skills/*.md; do
  sed -i.bak '/^---$/,/^---$/d' "$file"
done
# Restore index.json from git
git checkout .claude/skills/index.json
```

---

## Phase 2: Folder Structure Migration

**Duration**: 4-6 hours
**Risk**: Medium (file moves, path changes)
**Rollback**: Git revert

**Note**: Both formats coexist. Flat structure deprecated but still supported.

### 2.1 Create Folder Structure Template

**New directory structure**:
```
.claude/skills/
├── glp1-trials/                    # NEW: Folder structure
│   ├── SKILL.md                    # Moved from get_glp1_trials.md
│   └── scripts/
│       └── get_glp1_trials.py      # Moved from get_glp1_trials.py
│
├── glp1-fda-drugs/                 # NEW: Folder structure
│   ├── SKILL.md
│   └── scripts/
│       └── get_glp1_fda_drugs.py
│
├── get_kras_inhibitor_trials.py    # OLD: Flat structure (deprecated)
├── get_kras_inhibitor_trials.md    # OLD: Still works
└── index.json                      # Updated to reference both formats
```

### 2.2 Create init_skill.py Script

**File**: `.claude/scripts/init_skill.py`

```python
#!/usr/bin/env python3
"""Initialize a new skill in Anthropic folder structure format."""

import sys
import argparse
from pathlib import Path
from datetime import datetime

SKILL_MD_TEMPLATE = """---
name: {skill_name}
description: >
  [Describe what this skill does and when to use it. Be specific about:
   - What data source(s) it uses
   - What scope/coverage it provides
   - Special capabilities (pagination, filtering, etc.)
   - Keywords that trigger this skill usage]
category: clinical-trials
mcp_servers:
  - [server_name]
patterns:
  - [pattern_name]
data_scope:
  total_results: unknown
  geographical: unknown
  temporal: unknown
created: {created_date}
last_updated: {created_date}
complexity: simple
execution_time: ~N seconds
token_efficiency: ~99% reduction
---

# {skill_name}

## Purpose
[One-line description of what this skill accomplishes]

## Usage
**When to use this skill:**
- [Use case 1]
- [Use case 2]
- [Use case 3]

**Trigger keywords:** [list keywords that indicate this skill]

## Parameters
[If the function takes parameters, document them here]

## Returns
```python
{{
    'summary': 'Human-readable summary',
    'data': [...],  # Structured data
    'metadata': {{...}}  # Execution metadata
}}
```

## Implementation Details

### Data Source
- **MCP Server**: [server_name]
- **Response Format**: [JSON|Markdown]
- **Pagination**: [Yes|No]

### Key Features
- Feature 1
- Feature 2
- Feature 3

### Patterns Demonstrated
- Pattern 1: [description]
- Pattern 2: [description]

## Example Output
```
[Show example of what this skill returns]
```

## Related Skills
- `other-skill-name` - [how it relates]

## Notes
[Any important notes, limitations, or caveats]
"""

PYTHON_TEMPLATE = """import sys
sys.path.insert(0, "scripts")
from mcp.servers.{server_name} import {function_name}

def {skill_function_name}():
    \"\"\"[Brief description of what this function does].

    Returns:
        dict: Contains summary and structured data
    \"\"\"
    # TODO: Implement skill logic

    result = {function_name}()

    # Process and return
    return {{
        'summary': 'TODO: Human-readable summary',
        'data': result,
        'metadata': {{
            'source': '{server_name}',
            'timestamp': 'TODO: Add timestamp'
        }}
    }}

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    result = {skill_function_name}()
    print(result['summary'])
"""

def init_skill(skill_name: str, skill_folder_name: str = None, server: str = None):
    """Initialize a new skill with Anthropic folder structure.

    Args:
        skill_name: Python function name (e.g., get_glp1_trials)
        skill_folder_name: Folder name (e.g., glp1-trials). Defaults to skill_name with underscores->hyphens
        server: MCP server name (e.g., ct_gov_mcp)
    """
    # Generate folder name if not provided
    if skill_folder_name is None:
        skill_folder_name = skill_name.replace('_', '-')

    # Create directory structure
    skill_dir = Path(f".claude/skills/{skill_folder_name}")
    scripts_dir = skill_dir / "scripts"

    skill_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)

    # Create SKILL.md
    skill_md_content = SKILL_MD_TEMPLATE.format(
        skill_name=skill_name,
        created_date=datetime.now().strftime('%Y-%m-%d')
    )
    (skill_dir / "SKILL.md").write_text(skill_md_content)

    # Create Python script
    python_content = PYTHON_TEMPLATE.format(
        skill_function_name=skill_name,
        server_name=server or "server_name",
        function_name="function_name"
    )
    (scripts_dir / f"{skill_name}.py").write_text(python_content)

    print(f"✓ Skill initialized: .claude/skills/{skill_folder_name}")
    print(f"  - SKILL.md created with frontmatter template")
    print(f"  - scripts/{skill_name}.py created")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_dir}/SKILL.md to add metadata and documentation")
    print(f"  2. Implement logic in {scripts_dir}/{skill_name}.py")
    print(f"  3. Test: PYTHONPATH=scripts:$PYTHONPATH python3 {scripts_dir}/{skill_name}.py")

def main():
    parser = argparse.ArgumentParser(description='Initialize a new skill')
    parser.add_argument('skill_name', help='Python function name (e.g., get_glp1_trials)')
    parser.add_argument('--folder', help='Folder name (defaults to skill_name with hyphens)')
    parser.add_argument('--server', help='MCP server name (e.g., ct_gov_mcp)')

    args = parser.parse_args()
    init_skill(args.skill_name, args.folder, args.server)

if __name__ == "__main__":
    main()
```

**Test**:
```bash
python3 .claude/scripts/init_skill.py test_skill --server ct_gov_mcp
# Should create .claude/skills/test-skill/ with SKILL.md and scripts/
```

### 2.3 Create package_skill.py Script

**File**: `.claude/scripts/package_skill.py`

```python
#!/usr/bin/env python3
"""Migrate existing flat-structure skill to Anthropic folder structure."""

import sys
import shutil
import argparse
from pathlib import Path

def package_skill(skill_name: str, folder_name: str = None):
    """Migrate a flat skill to folder structure.

    Args:
        skill_name: Base name without extension (e.g., get_glp1_trials)
        folder_name: Target folder name (defaults to skill_name with hyphens)
    """
    # Generate folder name
    if folder_name is None:
        folder_name = skill_name.replace('_', '-')

    # Source files (flat structure)
    source_py = Path(f".claude/skills/{skill_name}.py")
    source_md = Path(f".claude/skills/{skill_name}.md")

    # Validate source files exist
    if not source_py.exists():
        print(f"Error: {source_py} not found")
        return False
    if not source_md.exists():
        print(f"Error: {source_md} not found")
        return False

    # Target directory (folder structure)
    target_dir = Path(f".claude/skills/{folder_name}")
    scripts_dir = target_dir / "scripts"

    # Check if already migrated
    if target_dir.exists():
        print(f"Warning: {target_dir} already exists. Skipping.")
        return False

    # Create directory structure
    target_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)

    # Move/rename files
    # .md becomes SKILL.md
    shutil.copy2(source_md, target_dir / "SKILL.md")

    # .py goes into scripts/
    shutil.copy2(source_py, scripts_dir / f"{skill_name}.py")

    # Keep originals for backward compatibility (deprecate later)
    print(f"✓ Packaged skill: {folder_name}")
    print(f"  Source: .claude/skills/{skill_name}.{{py,md}}")
    print(f"  Target: .claude/skills/{folder_name}/")
    print(f"    - SKILL.md")
    print(f"    - scripts/{skill_name}.py")
    print(f"\nNote: Original files kept for backward compatibility")
    print(f"      Mark as deprecated in index.json")

    return True

def main():
    parser = argparse.ArgumentParser(description='Package existing skill into folder structure')
    parser.add_argument('skill_name', help='Skill base name (e.g., get_glp1_trials)')
    parser.add_argument('--folder', help='Target folder name (defaults to skill_name with hyphens)')
    parser.add_argument('--remove-original', action='store_true',
                       help='Remove original files after migration (use with caution)')

    args = parser.parse_args()

    success = package_skill(args.skill_name, args.folder)

    if success and args.remove_original:
        # Remove originals
        Path(f".claude/skills/{args.skill_name}.py").unlink()
        Path(f".claude/skills/{args.skill_name}.md").unlink()
        print(f"  Removed original files (--remove-original)")

if __name__ == "__main__":
    main()
```

### 2.4 Migrate Reference Skills

**Order** (migrate best-documented skills first):

1. **glp1-trials** (get_glp1_trials)
   ```bash
   python3 .claude/scripts/package_skill.py get_glp1_trials --folder glp1-trials
   ```

2. **glp1-fda-drugs** (get_glp1_fda_drugs)
   ```bash
   python3 .claude/scripts/package_skill.py get_glp1_fda_drugs --folder glp1-fda-drugs
   ```

3. Test both structures work:
   ```bash
   # New structure
   PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/glp1-trials/scripts/get_glp1_trials.py

   # Old structure (should still work)
   PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_glp1_trials.py
   ```

4. Migrate remaining 9 skills (only if tests pass)

### 2.5 Update index.json for Dual Structure

**File**: `.claude/skills/index.json`

Add `structure` field to track format:

```json
{
  "version": "2.0",
  "format": "hybrid-transition",
  "description": "Both flat and folder structures supported during migration",
  "skills": [
    {
      "name": "get_glp1_trials",
      "structure": "folder",
      "folder": "glp1-trials",
      "skill_md": "glp1-trials/SKILL.md",
      "script": "glp1-trials/scripts/get_glp1_trials.py",
      "deprecated_files": {
        "py": "get_glp1_trials.py",
        "md": "get_glp1_trials.md",
        "status": "kept_for_compatibility"
      },
      ...
    },
    {
      "name": "get_kras_inhibitor_trials",
      "structure": "flat",
      "file": "get_kras_inhibitor_trials.py",
      "documentation": "get_kras_inhibitor_trials.md",
      "migration_status": "pending",
      ...
    }
  ]
}
```

### 2.6 Create Skill Discovery Utility

**File**: `.claude/scripts/discover_skills.py`

```python
#!/usr/bin/env python3
"""Discover available skills regardless of structure (flat or folder)."""

import json
from pathlib import Path
from typing import List, Dict
import sys
sys.path.insert(0, '.claude/scripts')
from parse_skill_metadata import parse_skill_frontmatter

def discover_skills() -> Dict[str, Dict]:
    """Discover all skills (both structures).

    Returns:
        Dictionary mapping skill names to skill info
    """
    skills_dir = Path('.claude/skills')
    discovered = {}

    # Check index.json first
    index_path = skills_dir / 'index.json'
    if index_path.exists():
        index = json.loads(index_path.read_text())

        for skill_info in index.get('skills', []):
            name = skill_info['name']
            structure = skill_info.get('structure', 'flat')

            if structure == 'folder':
                # Folder structure
                folder = skill_info.get('folder')
                skill_md_path = skills_dir / folder / 'SKILL.md'
                if skill_md_path.exists():
                    metadata = parse_skill_frontmatter(skill_md_path)
                    skill_info['metadata'] = metadata
                    discovered[name] = skill_info
            else:
                # Flat structure
                skill_md_path = skills_dir / skill_info.get('documentation')
                if skill_md_path.exists():
                    metadata = parse_skill_frontmatter(skill_md_path)
                    skill_info['metadata'] = metadata
                    discovered[name] = skill_info

    return discovered

def find_skill_by_pattern(pattern_name: str) -> List[str]:
    """Find skills that demonstrate a specific pattern.

    Args:
        pattern_name: Pattern to search for (e.g., 'pagination')

    Returns:
        List of skill names
    """
    skills = discover_skills()
    matching = []

    for name, info in skills.items():
        metadata = info.get('metadata', {})
        patterns = metadata.get('patterns', [])
        if pattern_name in patterns:
            matching.append(name)

    return matching

def find_skill_by_server(server_name: str) -> List[str]:
    """Find skills that use a specific MCP server.

    Args:
        server_name: MCP server name (e.g., 'ct_gov_mcp')

    Returns:
        List of skill names
    """
    skills = discover_skills()
    matching = []

    for name, info in skills.items():
        metadata = info.get('metadata', {})
        servers = metadata.get('mcp_servers', [])
        if server_name in servers:
            matching.append(name)

    return matching

if __name__ == "__main__":
    skills = discover_skills()
    print(f"Discovered {len(skills)} skills:\n")

    for name, info in sorted(skills.items()):
        structure = info.get('structure', 'unknown')
        metadata = info.get('metadata', {})
        category = metadata.get('category', 'unknown')
        complexity = metadata.get('complexity', 'unknown')

        print(f"  {name:40s} [{structure:6s}] {category:20s} ({complexity})")

    print(f"\n✓ All skills accessible regardless of structure")
```

**Test**:
```bash
python3 .claude/scripts/discover_skills.py
# Should list all skills (both flat and folder structures)
```

### 2.7 Phase 2 Testing

**Test Plan**:

1. **Validate folder structure**:
```bash
# Check both structures exist
ls -la .claude/skills/glp1-trials/
ls -la .claude/skills/get_kras_inhibitor_trials.py

# Verify files in correct locations
test -f .claude/skills/glp1-trials/SKILL.md
test -f .claude/skills/glp1-trials/scripts/get_glp1_trials.py
```

2. **Test execution (folder structure)**:
```bash
# New folder structure should work
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/glp1-trials/scripts/get_glp1_trials.py
```

3. **Test backward compatibility (flat structure)**:
```bash
# Old flat structure should still work
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/get_kras_inhibitor_trials.py
```

4. **Test skill discovery**:
```bash
python3 .claude/scripts/discover_skills.py
# Should show all skills regardless of structure

python3 -c "
from discover_skills import find_skill_by_pattern
skills = find_skill_by_pattern('pagination')
print(f'Skills with pagination: {skills}')
"
```

5. **Test imports still work**:
```python
# Test importing from both structures
import sys
sys.path.insert(0, 'scripts')
sys.path.insert(0, '.claude/skills/glp1-trials/scripts')

from get_glp1_trials import get_glp1_trials
result = get_glp1_trials()
assert result['total_count'] > 0
print("✓ Folder structure imports work")
```

**Success Criteria**:
- ✅ 2 reference skills migrated to folder structure
- ✅ Both structures execute correctly
- ✅ Skill discovery works for both formats
- ✅ Backward compatibility maintained (flat skills still work)
- ✅ index.json tracks both structures
- ✅ Scripts (init_skill, package_skill, discover_skills) all working

**Rollback Procedure**:
```bash
# Remove new folder structures
rm -rf .claude/skills/glp1-trials
rm -rf .claude/skills/glp1-fda-drugs

# Restore index.json
git checkout .claude/skills/index.json

# Original flat files remain untouched
```

---

## Phase 3: Update Agent Behavior

**Duration**: 3-4 hours
**Risk**: Medium (changes agent code generation)
**Rollback**: Git revert agent files

### 3.1 Update pharma-search-specialist Agent

**File**: `.claude/agents/pharma-search-specialist.md`

Add new section on skill generation:

```markdown
### Step 5: Return Skill Code in New Format

**IMPORTANT**: Generate skills in Anthropic folder structure format.

**Return structure**:
```
Folder: {skill_folder_name}/
├── SKILL.md (with YAML frontmatter)
└── scripts/{skill_function_name}.py
```

**YAML frontmatter template**:
\```yaml
---
name: {skill_function_name}
description: >
  {Detailed description with use cases and triggers}
category: {clinical-trials|drug-discovery|financial|regulatory}
mcp_servers:
  - {server_name}
patterns:
  - {pattern_name}
created: {YYYY-MM-DD}
complexity: {simple|medium|complex}
---
\```

**Return in your response**:

1. **Folder structure**:
\```
Skill folder: {skill-folder-name}/
\```

2. **SKILL.md** (complete):
\```markdown
---
name: get_example_data
description: >
  [Full description with use cases]
category: clinical-trials
...
---

# get_example_data

## Purpose
...
\```

3. **Python script** (complete):
\```python
import sys
sys.path.insert(0, "scripts")
from mcp.servers.{server} import {function}

def get_example_data():
    ...
\```

Main agent will:
1. Create folder: `.claude/skills/{skill-folder-name}/`
2. Write SKILL.md
3. Create scripts/ subdirectory
4. Write Python script
5. Update index.json
```

### 3.2 Update CLAUDE.md Documentation

**File**: `.claude/CLAUDE.md`

Update Directory Structure section:

```markdown
## Directory Structure

\```
.claude/
├── CLAUDE.md                           # This file - architecture overview
├── agents/
│   ├── pharma-search-specialist.md     # Infrastructure agent
│   └── competitive-landscape-analyst.md # Strategic agent
├── .context/
│   ├── mcp-tool-guides/                # MCP server API documentation
│   │   ├── clinicaltrials.md           # CT.gov API (returns markdown)
│   │   ├── fda.md                      # FDA API (returns JSON)
│   │   ├── pubmed.md
│   │   └── [10 more servers...]
│   ├── code-examples/                  # Code patterns (progressive disclosure)
│   │   ├── ctgov_markdown_parsing.md   # CT.gov pattern
│   │   ├── fda_json_parsing.md         # FDA pattern
│   │   ├── multi_server_query.md       # Combining servers
│   │   └── skills_library_pattern.md   # Skills library pattern
│   └── templates/                      # Report templates
│       ├── competitive-landscape-report.md
│       └── skill-frontmatter-template.yaml  # NEW
└── skills/                             # Reusable functions (built over time)
    ├── index.json                      # Skills discovery index
    │
    ├── glp1-trials/                    # NEW: Folder structure (Anthropic format)
    │   ├── SKILL.md                    # Metadata + documentation
    │   └── scripts/
    │       └── get_glp1_trials.py      # Executable function
    │
    ├── glp1-fda-drugs/                 # NEW: Folder structure
    │   ├── SKILL.md
    │   └── scripts/
    │       └── get_glp1_fda_drugs.py
    │
    └── get_old_skill.py                # OLD: Flat structure (deprecated)
        get_old_skill.md

scripts/                                # Utilities
├── init_skill.py                       # NEW: Initialize new skill
├── package_skill.py                    # NEW: Migrate flat to folder
├── discover_skills.py                  # NEW: Find skills (both formats)
└── mcp/                                # MCP infrastructure
    ├── client.py
    └── servers/
\```
```

Add new section on Skills Library Evolution:

```markdown
## Skills Library Evolution

### Format Transition (v1 → v2)

**v1 (Flat structure)** - Deprecated but still supported:
\```
.claude/skills/
├── get_glp1_trials.py
└── get_glp1_trials.md
\```

**v2 (Folder structure)** - Current standard (Anthropic format):
\```
.claude/skills/
└── glp1-trials/
    ├── SKILL.md              # YAML frontmatter + documentation
    └── scripts/
        └── get_glp1_trials.py
\```

### Skill Discovery

Agent discovers skills via:
1. **index.json** - Master registry (tracks both formats)
2. **YAML frontmatter** - Metadata in SKILL.md files
3. **discover_skills.py** - Utility for programmatic discovery

### Creating New Skills

**Manual**:
\```bash
python3 .claude/scripts/init_skill.py get_new_data --server ct_gov_mcp
\```

**Via Agent**:
User query → Agent generates folder structure → Main agent saves files

### Migrating Old Skills

\```bash
python3 .claude/scripts/package_skill.py get_old_skill --folder old-skill
\```
```

### 3.3 Update Skills Library Pattern Example

**File**: `.claude/.context/code-examples/skills_library_pattern.md`

Update to show new folder structure:

```markdown
## Complete Pattern (Folder Structure)

Agent generates and returns:

### 1. Folder name
\```
Skill: glp1-trials/
\```

### 2. SKILL.md (with frontmatter)
\```markdown
---
name: get_glp1_trials
description: >
  Collect comprehensive GLP-1 clinical trial data from ClinicalTrials.gov
  with full pagination support. Use when analyzing GLP-1 pipeline.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
created: 2025-11-19
complexity: medium
---

# get_glp1_trials

## Purpose
[Documentation continues...]
\```

### 3. Python script
\```python
# scripts/get_glp1_trials.py
import sys
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_glp1_trials():
    \"\"\"Get GLP-1 clinical trials.\"\"\"
    result = search(intervention="GLP-1")
    return result

if __name__ == "__main__":
    result = get_glp1_trials()
    print(result)
\```

## Main Agent Saves Files

Main Claude Code agent:
1. Creates folder: `.claude/skills/glp1-trials/`
2. Writes SKILL.md
3. Creates scripts/ subdirectory
4. Writes get_glp1_trials.py
5. Updates index.json
```

### 3.4 Create Main Agent Helper Functions

**File**: `.claude/scripts/save_skill.py`

```python
#!/usr/bin/env python3
"""Helper functions for main Claude Code agent to save skills."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict

def save_skill_folder_structure(
    skill_name: str,
    folder_name: str,
    skill_md_content: str,
    python_script_content: str
) -> bool:
    """Save skill in folder structure format.

    Args:
        skill_name: Python function name (e.g., get_glp1_trials)
        folder_name: Folder name (e.g., glp1-trials)
        skill_md_content: Complete SKILL.md content (with frontmatter)
        python_script_content: Complete Python script content

    Returns:
        True if successful
    """
    try:
        # Create directory structure
        skill_dir = Path(f".claude/skills/{folder_name}")
        scripts_dir = skill_dir / "scripts"

        skill_dir.mkdir(parents=True, exist_ok=True)
        scripts_dir.mkdir(exist_ok=True)

        # Write files
        (skill_dir / "SKILL.md").write_text(skill_md_content)
        (scripts_dir / f"{skill_name}.py").write_text(python_script_content)

        print(f"✓ Skill saved: .claude/skills/{folder_name}")
        return True

    except Exception as e:
        print(f"Error saving skill: {e}")
        return False

def update_skills_index(skill_info: Dict) -> bool:
    """Add skill to index.json.

    Args:
        skill_info: Skill metadata dictionary

    Returns:
        True if successful
    """
    try:
        index_path = Path(".claude/skills/index.json")

        # Read existing index
        if index_path.exists():
            index = json.loads(index_path.read_text())
        else:
            index = {
                "version": "2.0",
                "format": "folder-structure",
                "skills": []
            }

        # Add new skill
        index['skills'].append(skill_info)
        index['last_updated'] = datetime.now().isoformat()

        # Write back
        index_path.write_text(json.dumps(index, indent=2))

        print(f"✓ Updated index.json")
        return True

    except Exception as e:
        print(f"Error updating index: {e}")
        return False
```

### 3.5 Phase 3 Testing

**Test Plan**:

1. **Test agent generates new format**:
```bash
# Query that requires new skill
# Expected: Agent returns folder structure, SKILL.md, Python script
# Main agent uses save_skill_folder_structure() to save files
```

2. **Test skill discovery after agent creation**:
```bash
python3 .claude/scripts/discover_skills.py
# New skill should appear in list
```

3. **Test new skill execution**:
```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/new-skill/scripts/get_new_data.py
```

4. **Test backward compatibility** (agent can still use old flat skills):
```python
# Old skills should still be discoverable and usable
from discover_skills import discover_skills
skills = discover_skills()
# Should include both old (flat) and new (folder) skills
```

**Success Criteria**:
- ✅ Agent generates new folder structure format
- ✅ Main agent successfully saves files
- ✅ New skills execute correctly
- ✅ index.json updated automatically
- ✅ Old skills still work (backward compatibility)
- ✅ Documentation updated (CLAUDE.md, agent files)

**Rollback Procedure**:
```bash
# Revert agent changes
git checkout .claude/agents/pharma-search-specialist.md
git checkout .claude/CLAUDE.md
git checkout .claude/.context/code-examples/skills_library_pattern.md

# Remove helper script
rm .claude/scripts/save_skill.py

# New skills remain (no harm), just won't generate more
```

---

## Phase 4: Complete Migration & Cleanup

**Duration**: 2-3 hours
**Risk**: Low (cleanup only)
**Rollback**: Git revert (old files preserved in git history)

### 4.1 Migrate Remaining Skills

**Action**: Migrate all 9 remaining flat skills to folder structure

```bash
# Migrate each skill
for skill in get_kras_inhibitor_trials get_kras_inhibitor_fda_drugs get_glp1_diabetes_drugs get_covid19_vaccine_trials_recruiting get_phase2_alzheimers_trials_us get_us_phase3_obesity_recruiting_trials get_adc_trials get_braf_inhibitor_trials get_braf_inhibitor_fda_drugs; do
  folder=$(echo $skill | sed 's/_/-/g')
  python3 .claude/scripts/package_skill.py $skill --folder $folder
done
```

**Test after each migration**:
```bash
# Verify execution
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/$folder/scripts/$skill.py
```

### 4.2 Mark Flat Structure as Deprecated

**Update index.json**:
```json
{
  "version": "2.0",
  "format": "folder-structure",
  "deprecated_format": "flat",
  "migration_complete": true,
  "migration_date": "2025-11-XX",
  "skills": [
    {
      "name": "get_glp1_trials",
      "structure": "folder",
      "folder": "glp1-trials",
      ...
      "deprecated_files": {
        "status": "scheduled_for_removal",
        "removal_date": "2025-12-XX"
      }
    }
  ]
}
```

### 4.3 Add Deprecation Notice to README

**File**: `.claude/skills/README.md`

```markdown
# Skills Library

Reusable pharmaceutical intelligence data collection functions.

## Structure (v2.0)

Skills use **Anthropic folder structure** format:

\```
skill-name/
├── SKILL.md              # YAML frontmatter + documentation
└── scripts/
    └── skill_function.py # Executable Python function
\```

## Discovering Skills

\```bash
# List all available skills
python3 .claude/scripts/discover_skills.py

# Find skills by pattern
python3 -c "from discover_skills import find_skill_by_pattern; print(find_skill_by_pattern('pagination'))"

# Find skills by MCP server
python3 -c "from discover_skills import find_skill_by_server; print(find_skill_by_server('ct_gov_mcp'))"
\```

## Creating New Skills

\```bash
# Initialize new skill
python3 .claude/scripts/init_skill.py get_new_data --server ct_gov_mcp --folder new-data

# Edit SKILL.md and implement logic in scripts/
\```

## Deprecated (v1.0 Flat Structure)

**Note**: Flat structure (.py + .md pairs in root) is **deprecated** as of 2025-11-XX.

Old flat files will be removed on 2025-12-XX. Migrate using:

\```bash
python3 .claude/scripts/package_skill.py old_skill_name --folder new-skill-name
\```

## Migration Status

- ✅ All 11 skills migrated to folder structure
- ⚠️ Flat files kept for 30 days (removal: 2025-12-XX)
- ✅ Backward compatibility: Old imports still work during transition
```

### 4.4 Schedule Flat File Removal

**Create cleanup script**: `.claude/scripts/cleanup_deprecated_skills.py`

```python
#!/usr/bin/env python3
"""Remove deprecated flat structure skill files."""

import json
from pathlib import Path
from datetime import datetime

def cleanup_deprecated_skills(dry_run=True):
    """Remove flat structure files that have been migrated.

    Args:
        dry_run: If True, only show what would be deleted
    """
    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    if not index.get('migration_complete'):
        print("Migration not complete. Aborting cleanup.")
        return

    removal_date = index.get('deprecated_files', {}).get('removal_date')
    if removal_date and datetime.now() < datetime.fromisoformat(removal_date):
        print(f"Removal scheduled for {removal_date}. Not yet time.")
        return

    removed = []
    for skill in index['skills']:
        deprecated = skill.get('deprecated_files', {})
        if deprecated.get('status') == 'scheduled_for_removal':
            # Remove flat files
            py_file = Path(f".claude/skills/{deprecated['py']}")
            md_file = Path(f".claude/skills/{deprecated['md']}")

            if dry_run:
                print(f"Would remove: {py_file}, {md_file}")
            else:
                if py_file.exists():
                    py_file.unlink()
                if md_file.exists():
                    md_file.unlink()
                print(f"Removed: {py_file}, {md_file}")

            removed.append(skill['name'])

    print(f"\n{'Would remove' if dry_run else 'Removed'} {len(removed)} deprecated file pairs")

    if not dry_run:
        # Update index to remove deprecated_files entries
        for skill in index['skills']:
            if 'deprecated_files' in skill:
                del skill['deprecated_files']
        index['cleanup_date'] = datetime.now().isoformat()
        index_path.write_text(json.dumps(index, indent=2))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true',
                       help='Actually delete files (default is dry-run)')
    args = parser.parse_args()

    cleanup_deprecated_skills(dry_run=not args.execute)
```

### 4.5 Phase 4 Testing

**Test Plan**:

1. **Verify all skills migrated**:
```bash
python3 .claude/scripts/discover_skills.py
# Should show 11 skills, all with structure="folder"
```

2. **Test all skills execute**:
```bash
for skill_dir in .claude/skills/*/; do
  if [ -d "$skill_dir/scripts" ]; then
    script=$(ls $skill_dir/scripts/*.py | head -1)
    echo "Testing $script..."
    PYTHONPATH=scripts:$PYTHONPATH python3 $script || echo "FAILED: $script"
  fi
done
```

3. **Test cleanup script (dry-run)**:
```bash
python3 .claude/scripts/cleanup_deprecated_skills.py
# Should list files that would be removed
```

4. **Verify documentation complete**:
```bash
# Check all expected docs exist
test -f .claude/skills/README.md
test -f .claude/.context/anthropic-skills-migration-plan.md
grep -q "folder structure" .claude/CLAUDE.md
```

**Success Criteria**:
- ✅ All 11 skills migrated to folder structure
- ✅ All skills execute successfully
- ✅ Flat files marked for removal
- ✅ Documentation updated (README, CLAUDE.md)
- ✅ Cleanup script ready (scheduled for 30 days)
- ✅ index.json reflects migration complete

**Final Cleanup** (after 30-day grace period):
```bash
# After removal_date passes
python3 .claude/scripts/cleanup_deprecated_skills.py --execute
```

---

## Testing Strategy

### Integration Testing (After Each Phase)

**Test Suite**: `.claude/scripts/test_skills_migration.py`

```python
#!/usr/bin/env python3
"""Integration tests for skills migration."""

import sys
import json
from pathlib import Path

sys.path.insert(0, '.claude/scripts')
from discover_skills import discover_skills, find_skill_by_pattern
from parse_skill_metadata import parse_skill_frontmatter

def test_phase1_frontmatter():
    """Test Phase 1: YAML frontmatter added."""
    print("Testing Phase 1: YAML Frontmatter...")

    skills_dir = Path('.claude/skills')
    skill_mds = list(skills_dir.glob('*/SKILL.md')) + list(skills_dir.glob('*.md'))
    skill_mds = [f for f in skill_mds if f.name != 'README.md']

    passed = 0
    for md_file in skill_mds:
        metadata = parse_skill_frontmatter(md_file)
        if metadata:
            assert 'name' in metadata, f"{md_file}: missing 'name'"
            assert 'description' in metadata, f"{md_file}: missing 'description'"
            assert 'category' in metadata, f"{md_file}: missing 'category'"
            passed += 1

    print(f"  ✓ {passed}/{len(skill_mds)} skills have valid frontmatter")
    return passed == len(skill_mds)

def test_phase2_folder_structure():
    """Test Phase 2: Folder structure works."""
    print("Testing Phase 2: Folder Structure...")

    # Check expected folders exist
    expected_folders = ['glp1-trials', 'glp1-fda-drugs']
    for folder in expected_folders:
        skill_dir = Path(f'.claude/skills/{folder}')
        assert skill_dir.exists(), f"{folder} not found"
        assert (skill_dir / 'SKILL.md').exists(), f"{folder}/SKILL.md not found"
        assert (skill_dir / 'scripts').exists(), f"{folder}/scripts/ not found"

        # Check Python script exists
        scripts = list((skill_dir / 'scripts').glob('*.py'))
        assert len(scripts) > 0, f"{folder}/scripts/ has no Python files"

    print(f"  ✓ {len(expected_folders)} folder-structured skills valid")
    return True

def test_phase3_agent_behavior():
    """Test Phase 3: Agent behavior updated."""
    print("Testing Phase 3: Agent Behavior...")

    # Check agent files updated
    agent_file = Path('.claude/agents/pharma-search-specialist.md')
    content = agent_file.read_text()

    assert 'folder structure' in content.lower(), "Agent not updated for folder structure"
    assert 'SKILL.md' in content, "Agent doesn't mention SKILL.md"

    # Check CLAUDE.md updated
    claude_md = Path('.claude/CLAUDE.md')
    content = claude_md.read_text()

    assert 'folder structure' in content.lower() or 'Anthropic format' in content, \
           "CLAUDE.md not updated"

    print("  ✓ Agent files and documentation updated")
    return True

def test_phase4_migration_complete():
    """Test Phase 4: Migration complete."""
    print("Testing Phase 4: Migration Complete...")

    skills = discover_skills()
    folder_count = sum(1 for s in skills.values() if s.get('structure') == 'folder')
    total_count = len(skills)

    print(f"  Migration status: {folder_count}/{total_count} skills in folder structure")

    # Check README updated
    readme = Path('.claude/skills/README.md')
    if readme.exists():
        content = readme.read_text()
        assert 'deprecated' in content.lower(), "README doesn't mention deprecation"
        print("  ✓ README updated with deprecation notice")

    return folder_count == total_count

def run_all_tests():
    """Run all phase tests."""
    print("="*60)
    print("Skills Migration Test Suite")
    print("="*60 + "\n")

    tests = [
        ("Phase 1", test_phase1_frontmatter),
        ("Phase 2", test_phase2_folder_structure),
        ("Phase 3", test_phase3_agent_behavior),
        ("Phase 4", test_phase4_migration_complete),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
            print()
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}\n")
            results[name] = False
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results[name] = False

    print("="*60)
    print("Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    print("="*60)

    return all(results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

**Run after each phase**:
```bash
python3 .claude/scripts/test_skills_migration.py
```

---

## Rollback Procedures

### Emergency Rollback (Any Phase)

```bash
# Full rollback to pre-migration state
git checkout .claude/agents/
git checkout .claude/CLAUDE.md
git checkout .claude/.context/
git checkout .claude/skills/

# Remove new scripts
rm .claude/scripts/init_skill.py
rm .claude/scripts/package_skill.py
rm .claude/scripts/discover_skills.py
rm .claude/scripts/save_skill.py
rm .claude/scripts/test_skills_migration.py

# Remove new folders
rm -rf .claude/skills/*/

# Skills remain functional (flat files never deleted during migration)
```

### Phase-Specific Rollback

**Phase 1**: Remove frontmatter
```bash
for file in .claude/skills/*.md; do
  sed -i.bak '/^---$/,/^---$/d' "$file"
done
git checkout .claude/skills/index.json
```

**Phase 2**: Remove folders, restore index
```bash
rm -rf .claude/skills/*/
git checkout .claude/skills/index.json
```

**Phase 3**: Revert agent changes
```bash
git checkout .claude/agents/
git checkout .claude/CLAUDE.md
git checkout .claude/.context/
```

**Phase 4**: Restore flat files
```bash
git checkout .claude/skills/*.py
git checkout .claude/skills/*.md
```

---

## Timeline

### Week 1: Foundation
- **Day 1-2**: Phase 1 (YAML frontmatter) - 2-3 hours
- **Day 3**: Testing & validation - 1 hour
- **Day 4-5**: Phase 2 (folder structure, 2 skills) - 4-6 hours

### Week 2: Agent Updates
- **Day 1-2**: Phase 2 continued (test & validate) - 2 hours
- **Day 3-4**: Phase 3 (agent behavior) - 3-4 hours
- **Day 5**: Testing & validation - 2 hours

### Week 3: Complete Migration
- **Day 1-2**: Phase 4 (migrate remaining 9 skills) - 2-3 hours
- **Day 3-4**: Testing, documentation, cleanup scripts - 2 hours
- **Day 5**: Final validation & documentation - 1 hour

### Week 4+: Grace Period
- 30-day grace period before removing flat files
- Monitor for issues, help users adapt
- Execute cleanup after grace period

---

## Success Metrics

### Phase 1 Success
- ✅ 11/11 skills have valid YAML frontmatter
- ✅ All skills still executable (backward compatible)
- ✅ Parser utility works
- ✅ No user-facing changes

### Phase 2 Success
- ✅ 2 reference skills in folder structure
- ✅ Both structures work (flat + folder)
- ✅ Discovery works for both formats
- ✅ Scripts (init, package, discover) functional

### Phase 3 Success
- ✅ Agent generates folder structure
- ✅ Main agent saves correctly
- ✅ Documentation updated
- ✅ Old skills still usable

### Phase 4 Success
- ✅ All 11 skills migrated
- ✅ Flat structure deprecated
- ✅ Cleanup scheduled
- ✅ All tests passing

### Overall Success
- ✅ Zero breaking changes during migration
- ✅ All skills executable throughout process
- ✅ Agent behavior improved (generates new format)
- ✅ Documentation complete and accurate
- ✅ Clear migration path for future skills

---

## Files Modified/Created

### New Files Created

**Scripts**:
- `.claude/scripts/init_skill.py` - Initialize new skills
- `.claude/scripts/package_skill.py` - Migrate flat to folder
- `.claude/scripts/discover_skills.py` - Skill discovery utility
- `.claude/scripts/parse_skill_metadata.py` - Frontmatter parser
- `.claude/scripts/save_skill.py` - Main agent helper
- `.claude/scripts/test_skills_migration.py` - Integration tests
- `.claude/scripts/cleanup_deprecated_skills.py` - Cleanup utility

**Templates**:
- `.claude/.context/templates/skill-frontmatter-template.yaml` - YAML template

**Documentation**:
- `.claude/.context/anthropic-skills-migration-plan.md` - This file

**Skills** (new structure):
- `.claude/skills/glp1-trials/` (and 10 others)

### Files Modified

**Skills** (add frontmatter):
- `.claude/skills/*.md` (11 files) - Add YAML frontmatter

**Core Documentation**:
- `.claude/CLAUDE.md` - Update directory structure, add migration info
- `.claude/skills/README.md` - Add structure docs, deprecation notice
- `.claude/skills/index.json` - Add structure tracking, migration status

**Agent**:
- `.claude/agents/pharma-search-specialist.md` - Update skill generation

**Code Examples**:
- `.claude/.context/code-examples/skills_library_pattern.md` - Show folder structure

### Files Deprecated (Removed in Phase 4)

After 30-day grace period:
- `.claude/skills/get_*.py` (11 files)
- `.claude/skills/get_*.md` (11 files)

(Folders in skills/ directory replace these)

---

## Questions & Decisions

### Decision Points

**Q1**: Should we keep flat files during transition?
**A**: Yes, keep for 30 days for backward compatibility. Schedule cleanup.

**Q2**: Should we migrate all skills at once or gradually?
**A**: Gradually. Migrate 2 reference skills first, validate, then rest.

**Q3**: Should agent generate both formats?
**A**: No, agent should only generate new format. Old format deprecated.

**Q4**: What if users have local modifications to flat files?
**A**: Keep originals as .bak files during migration. Document in README.

**Q5**: Should we update all documentation immediately?
**A**: Yes in Phase 3, so documentation matches agent behavior.

---

## Communication Plan

### User-Facing Changes

**What users will notice**:
1. New skills appear in folder structure
2. Old skills still work (no disruption)
3. Better skill discovery (via frontmatter metadata)
4. Clearer skill documentation (SKILL.md)

**What users won't notice**:
- Internal reorganization
- Migration scripts
- Backward compatibility work

### Documentation Updates

**Immediate** (Phase 1-2):
- Add migration plan document
- Update README with structure info

**Phase 3**:
- Update CLAUDE.md
- Update agent files
- Update code examples

**Phase 4**:
- Add deprecation notices
- Document cleanup timeline
- Final status update

---

## Appendix: Command Reference

### Useful Commands

**Discover skills**:
```bash
python3 .claude/scripts/discover_skills.py
```

**Find skills by pattern**:
```bash
python3 -c "from discover_skills import find_skill_by_pattern; print(find_skill_by_pattern('pagination'))"
```

**Test skill execution**:
```bash
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/skill-name/scripts/function.py
```

**Parse frontmatter**:
```bash
python3 -c "
from pathlib import Path
from parse_skill_metadata import parse_skill_frontmatter
meta = parse_skill_frontmatter(Path('.claude/skills/skill-name/SKILL.md'))
print(meta)
"
```

**Run migration tests**:
```bash
python3 .claude/scripts/test_skills_migration.py
```

**Initialize new skill**:
```bash
python3 .claude/scripts/init_skill.py new_skill_name --server ct_gov_mcp
```

**Migrate existing skill**:
```bash
python3 .claude/scripts/package_skill.py old_skill_name --folder new-skill-name
```

### Git Workflow

**Before each phase**:
```bash
git checkout -b phase-N-migration
git add .
git commit -m "Phase N: [description]"
```

**After testing**:
```bash
git checkout main
git merge phase-N-migration
git tag phase-N-complete
git push origin main --tags
```

**Rollback**:
```bash
git checkout main
git revert HEAD  # or git reset --hard phase-N-complete
```

---

## End of Migration Plan

**Next Steps**:
1. Review this plan
2. Get approval to proceed
3. Start Phase 1 (YAML frontmatter)
4. Test thoroughly after each phase
5. Monitor for issues
6. Complete migration over 3 weeks
