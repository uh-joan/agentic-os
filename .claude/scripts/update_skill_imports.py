#!/usr/bin/env python3
"""Update all SKILL.md files to use folder structure imports."""

import re
from pathlib import Path

def update_skill_md(skill_folder: Path, function_name: str):
    """Update a single SKILL.md file with correct folder structure import."""

    skill_md = skill_folder / 'SKILL.md'

    if not skill_md.exists():
        print(f"  ✗ {skill_folder.name}/SKILL.md not found")
        return False

    content = skill_md.read_text()

    # Old pattern: from .claude.skills.get_function_name import get_function_name
    old_pattern = f"from .claude.skills.{function_name} import {function_name}"

    # New pattern: from .claude.skills.folder_name.scripts.function_name import function_name
    folder_name = skill_folder.name.replace('-', '_')
    new_pattern = f"from .claude.skills.{folder_name}.scripts.{function_name} import {function_name}"

    if old_pattern in content:
        updated_content = content.replace(old_pattern, new_pattern)
        skill_md.write_text(updated_content)
        print(f"  ✓ Updated {skill_folder.name}/SKILL.md")
        return True
    elif new_pattern in content:
        print(f"  ⊙ {skill_folder.name}/SKILL.md already updated")
        return True
    else:
        print(f"  ⚠ {skill_folder.name}/SKILL.md: no matching import found")
        return False

def update_all_skill_mds():
    """Update all SKILL.md files in folder structure."""

    skills_dir = Path('.claude/skills')

    # Map folder names to function names
    skills = [
        ('glp1-trials', 'get_glp1_trials'),
        ('glp1-fda-drugs', 'get_glp1_fda_drugs'),
        ('kras-inhibitor-trials', 'get_kras_inhibitor_trials'),
        ('kras-inhibitor-fda-drugs', 'get_kras_inhibitor_fda_drugs'),
        ('glp1-diabetes-drugs', 'get_glp1_diabetes_drugs'),
        ('covid19-vaccine-trials-recruiting', 'get_covid19_vaccine_trials_recruiting'),
        ('phase2-alzheimers-trials-us', 'get_phase2_alzheimers_trials_us'),
        ('us-phase3-obesity-recruiting-trials', 'get_us_phase3_obesity_recruiting_trials'),
        ('adc-trials', 'get_adc_trials'),
        ('braf-inhibitor-trials', 'get_braf_inhibitor_trials'),
        ('braf-inhibitor-fda-drugs', 'get_braf_inhibitor_fda_drugs'),
    ]

    updated = 0
    for folder_name, function_name in skills:
        skill_folder = skills_dir / folder_name
        if update_skill_md(skill_folder, function_name):
            updated += 1

    return updated

if __name__ == "__main__":
    print("="*60)
    print("Updating SKILL.md Files - Folder Structure Imports")
    print("="*60 + "\n")

    updated = update_all_skill_mds()

    print(f"\n✓ Updated {updated}/11 SKILL.md files")
    print("="*60)
