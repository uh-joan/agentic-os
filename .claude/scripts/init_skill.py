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
token_efficiency: ~99% reduction vs raw data
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
