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

    # Copy files
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
