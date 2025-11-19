#!/usr/bin/env python3
"""Parse YAML frontmatter from skill documentation files."""

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
        # Try using yaml if available
        try:
            import yaml
            metadata = yaml.safe_load(frontmatter_text)
            return metadata
        except ImportError:
            # Fallback to simple parsing
            metadata = {}
            for line in frontmatter_text.strip().split('\n'):
                if ':' in line and not line.startswith(' '):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle lists
                    if value.startswith('['):
                        value = value.strip('[]').split(',')
                        value = [v.strip().strip('"\'') for v in value]
                    # Handle multiline strings (description with >)
                    elif value == '>':
                        continue  # Skip, handled separately
                    # Handle simple values
                    else:
                        value = value.strip('"\'')

                    metadata[key] = value
                elif line.startswith('  - ') and key:
                    # List item
                    if not isinstance(metadata.get(key), list):
                        metadata[key] = []
                    metadata[key].append(line.strip('- ').strip())

            return metadata
    except Exception as e:
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
