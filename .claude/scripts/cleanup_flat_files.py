#!/usr/bin/env python3
"""Clean up deprecated flat files after migration to folder structure."""

import shutil
from pathlib import Path
from datetime import datetime

def cleanup_flat_files():
    """Move deprecated flat files to deprecated/ folder."""

    skills_dir = Path('.claude/skills')
    deprecated_dir = skills_dir / 'deprecated'

    # Create deprecated directory
    deprecated_dir.mkdir(exist_ok=True)

    # Create README in deprecated folder
    readme_content = f"""# Deprecated Skills (Flat Structure)

**Deprecation Date**: 2025-11-19
**Removal Date**: 2025-12-19 (30-day grace period)
**Reason**: Migration to Anthropic folder structure format

## What Happened?

All skills have been migrated from flat structure to Anthropic's folder structure format:

**Old (Flat)**:
```
.claude/skills/
├── get_skill_name.py
└── get_skill_name.md
```

**New (Folder)**:
```
.claude/skills/
└── skill-name/
    ├── SKILL.md (with YAML frontmatter)
    └── scripts/
        └── get_skill_name.py
```

## Migration Complete

All 11 skills have been successfully migrated to folder structure:
- glp1-trials/
- glp1-fda-drugs/
- kras-inhibitor-trials/
- kras-inhibitor-fda-drugs/
- glp1-diabetes-drugs/
- covid19-vaccine-trials-recruiting/
- phase2-alzheimers-trials-us/
- us-phase3-obesity-recruiting-trials/
- adc-trials/
- braf-inhibitor-trials/
- braf-inhibitor-fda-drugs/

## Accessing Folder Structure Skills

Use folder structure imports:
```python
# Example: GLP-1 trials skill
from .claude.skills.glp1_trials.scripts.get_glp1_trials import get_glp1_trials

# Or execute directly
PYTHONPATH=scripts:$PYTHONPATH python3 .claude/skills/glp1-trials/scripts/get_glp1_trials.py
```

## Files in This Folder

These files are kept for the 30-day grace period and will be removed on 2025-12-19.
All functionality has been preserved in the folder structure versions.

**DO NOT USE** these deprecated files. Use the folder structure versions instead.
"""

    (deprecated_dir / 'README.md').write_text(readme_content)

    # List of flat files to move
    flat_files = [
        'get_glp1_trials.py',
        'get_glp1_trials.md',
        'get_glp1_fda_drugs.py',
        'get_glp1_fda_drugs.md',
        'get_kras_inhibitor_trials.py',
        'get_kras_inhibitor_trials.md',
        'get_kras_inhibitor_fda_drugs.py',
        'get_kras_inhibitor_fda_drugs.md',
        'get_glp1_diabetes_drugs.py',
        'get_glp1_diabetes_drugs.md',
        'get_covid19_vaccine_trials_recruiting.py',
        'get_covid19_vaccine_trials_recruiting.md',
        'get_phase2_alzheimers_trials_us.py',
        'get_phase2_alzheimers_trials_us.md',
        'get_us_phase3_obesity_recruiting_trials.py',
        'get_us_phase3_obesity_recruiting_trials.md',
        'get_adc_trials.py',
        'get_adc_trials.md',
        'get_braf_inhibitor_trials.py',
        'get_braf_inhibitor_trials.md',
        'get_braf_inhibitor_fda_drugs.py',
        'get_braf_inhibitor_fda_drugs.md',
    ]

    moved = 0
    for flat_file in flat_files:
        source = skills_dir / flat_file
        target = deprecated_dir / flat_file

        if source.exists():
            shutil.move(str(source), str(target))
            print(f"  ✓ Moved {flat_file} → deprecated/")
            moved += 1
        else:
            print(f"  ⊙ {flat_file} not found (already moved?)")

    print(f"\n✓ Moved {moved} deprecated files to .claude/skills/deprecated/")
    print(f"✓ Files will be removed on 2025-12-19 (30-day grace period)")
    print(f"\nFolder structure:")
    print(f"  .claude/skills/")
    print(f"  ├── [11 folder structure skills]")
    print(f"  ├── deprecated/")
    print(f"  │   ├── README.md")
    print(f"  │   └── [22 deprecated flat files]")
    print(f"  └── index.json (v2.0)")

if __name__ == "__main__":
    print("="*60)
    print("Cleaning Up Deprecated Flat Files")
    print("="*60 + "\n")

    cleanup_flat_files()

    print("\n" + "="*60)
    print("Cleanup Complete")
    print("="*60)
