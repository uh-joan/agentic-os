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

            # Skip if we already have this skill in folder structure
            # (prefer folder over flat when there are duplicates)
            if name in discovered and discovered[name].get('structure') == 'folder':
                continue

            if structure == 'folder':
                # Folder structure
                folder = skill_info.get('folder')
                skill_md_path = skills_dir / folder / 'SKILL.md'
                if skill_md_path.exists():
                    metadata = parse_skill_frontmatter(skill_md_path)
                    skill_info['metadata'] = metadata
                    skill_info['skill_path'] = str(skill_md_path)
                    discovered[name] = skill_info
            else:
                # Flat structure
                skill_md_path = skills_dir / skill_info.get('documentation', f"{name}.md")
                if skill_md_path.exists():
                    metadata = parse_skill_frontmatter(skill_md_path)
                    skill_info['metadata'] = metadata
                    skill_info['skill_path'] = str(skill_md_path)
                    discovered[name] = skill_info

    # Also discover any folder-structure skills not in index
    for folder in skills_dir.iterdir():
        if folder.is_dir() and (folder / 'SKILL.md').exists():
            skill_md = folder / 'SKILL.md'
            metadata = parse_skill_frontmatter(skill_md)
            if metadata and metadata.get('name') not in discovered:
                # Found a folder skill not in index
                discovered[metadata['name']] = {
                    'name': metadata['name'],
                    'structure': 'folder',
                    'folder': folder.name,
                    'skill_path': str(skill_md),
                    'metadata': metadata
                }

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

def find_skill_by_category(category: str) -> List[str]:
    """Find skills in a specific category.

    Args:
        category: Category name (e.g., 'clinical-trials', 'drug-discovery')

    Returns:
        List of skill names
    """
    skills = discover_skills()
    matching = []

    for name, info in skills.items():
        metadata = info.get('metadata', {})
        if metadata.get('category') == category:
            matching.append(name)

    return matching

if __name__ == "__main__":
    skills = discover_skills()
    print(f"Discovered {len(skills)} skills:\n")

    # Group by structure
    flat_skills = []
    folder_skills = []

    for name, info in sorted(skills.items()):
        structure = info.get('structure', 'unknown')
        metadata = info.get('metadata', {})
        category = metadata.get('category', 'unknown')
        complexity = metadata.get('complexity', 'unknown')

        if structure == 'folder':
            folder_skills.append((name, category, complexity))
        else:
            flat_skills.append((name, category, complexity))

    if folder_skills:
        print(f"Folder Structure ({len(folder_skills)}):")
        for name, category, complexity in folder_skills:
            print(f"  {name:40s} {category:20s} ({complexity})")
        print()

    if flat_skills:
        print(f"Flat Structure ({len(flat_skills)}):")
        for name, category, complexity in flat_skills:
            print(f"  {name:40s} {category:20s} ({complexity})")
        print()

    print(f"✓ All skills accessible regardless of structure")

    # Show pattern distribution
    print(f"\nPattern Distribution:")
    patterns = {}
    for name, info in skills.items():
        metadata = info.get('metadata', {})
        for pattern in metadata.get('patterns', []):
            patterns[pattern] = patterns.get(pattern, 0) + 1

    for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
        print(f"  {pattern:30s}: {count} skills")
