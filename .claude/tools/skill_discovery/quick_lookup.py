"""
Quick Skill Lookup Utility

Fast direct lookup by exact skill name without strategy overhead.
Use this for known skills before falling back to strategy decision tree.
"""

import json
from pathlib import Path
from typing import Optional


def find_skill_by_name(skill_name: str) -> Optional[dict]:
    """Find skill by exact name match in index.

    This is the fastest lookup method - O(n) linear search through index.
    Use before invoking full strategy decision tree for known skills.

    Args:
        skill_name: Exact skill name (e.g., 'generate_drug_swot_analysis')

    Returns:
        Skill metadata dict if found, None otherwise

    Examples:
        >>> skill = find_skill_by_name('generate_drug_swot_analysis')
        >>> if skill:
        ...     print(f"Found: {skill['script']}")
        Found: drug-swot-analysis/scripts/generate_drug_swot_analysis.py

        >>> skill = find_skill_by_name('nonexistent_skill')
        >>> skill is None
        True
    """
    index_path = Path('.claude/skills/index.json')

    if not index_path.exists():
        return None

    try:
        index = json.loads(index_path.read_text())
    except (json.JSONDecodeError, IOError):
        return None

    # Linear search through skills (fast enough for ~100 skills)
    for skill in index.get('skills', []):
        if skill.get('name') == skill_name:
            return skill

    return None


def is_skill_healthy(skill: dict) -> bool:
    """Check if skill is healthy and ready to execute.

    Args:
        skill: Skill metadata dict from index

    Returns:
        True if skill is healthy or health status unknown, False if broken
    """
    health = skill.get('health', {})
    status = health.get('status', 'unknown')

    # Unknown status is treated as healthy (benefit of doubt)
    # Only explicitly broken skills return False
    return status != 'broken'


def get_cli_command(skill: dict, **kwargs) -> Optional[str]:
    """Build CLI command from skill metadata and arguments.

    Uses cli_format and cli_signature from index to construct correct command.

    Args:
        skill: Skill metadata dict from index
        **kwargs: Argument name-value pairs

    Returns:
        Complete command string ready to execute, or None if CLI not enabled

    Examples:
        >>> skill = find_skill_by_name('generate_drug_swot_analysis')
        >>> cmd = get_cli_command(skill, drug_name='semaglutide', indication='diabetes')
        >>> print(cmd)
        PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/drug-swot-analysis/scripts/generate_drug_swot_analysis.py semaglutide diabetes

        >>> skill = find_skill_by_name('get_disease_genetic_targets')
        >>> cmd = get_cli_command(skill, disease_name='Alzheimer\'s disease', top_n=10)
        >>> print(cmd)
        PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/disease-genetic-targets/scripts/get_disease_genetic_targets.py "Alzheimer's disease" --top-n 10
    """
    if not skill.get('cli_enabled'):
        return None

    script = skill.get('script')
    if not script:
        return None

    cli_format = skill.get('cli_format', 'unknown')

    # Build command based on format
    base_cmd = f"PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/{script}"

    if cli_format == 'positional':
        # Positional arguments - use values in order provided
        args = ' '.join(str(v) for v in kwargs.values())
        return f"{base_cmd} {args}"

    elif cli_format == 'argparse':
        # Named arguments - use --key value format
        args = ' '.join(f"--{k.replace('_', '-')} {v}" for k, v in kwargs.items())
        return f"{base_cmd} {args}"

    else:
        # Unknown format - try to execute with no args or kwargs
        if kwargs:
            # Best guess: try named arguments
            args = ' '.join(f"--{k.replace('_', '-')} {v}" for k, v in kwargs.items())
            return f"{base_cmd} {args}"
        return base_cmd


def quick_skill_lookup(skill_name: str) -> dict:
    """Complete quick lookup workflow with health check and execution readiness.

    This is the recommended high-level function for fast skill discovery.
    Returns comprehensive status to inform execution decision.

    Args:
        skill_name: Exact skill name to find

    Returns:
        Dict with status information:
        {
            'found': bool,
            'skill': dict or None,
            'healthy': bool,
            'ready_to_execute': bool,
            'reason': str (explanation of status)
        }

    Examples:
        >>> result = quick_skill_lookup('generate_drug_swot_analysis')
        >>> if result['ready_to_execute']:
        ...     skill = result['skill']
        ...     cmd = get_cli_command(skill, drug_name='semaglutide', indication='diabetes')
        ...     # Execute cmd via Bash tool
    """
    skill = find_skill_by_name(skill_name)

    if not skill:
        return {
            'found': False,
            'skill': None,
            'healthy': False,
            'ready_to_execute': False,
            'reason': f"Skill '{skill_name}' not found in index"
        }

    healthy = is_skill_healthy(skill)

    if not healthy:
        return {
            'found': True,
            'skill': skill,
            'healthy': False,
            'ready_to_execute': False,
            'reason': f"Skill found but marked as broken: {skill.get('health', {}).get('issues', [])}"
        }

    return {
        'found': True,
        'skill': skill,
        'healthy': True,
        'ready_to_execute': True,
        'reason': f"Skill found and healthy - ready to execute"
    }


# CLI interface for testing
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Quick skill lookup by name')
    parser.add_argument('skill_name', help='Exact skill name to find')
    parser.add_argument('--json', action='store_true', help='Output JSON')

    args = parser.parse_args()

    result = quick_skill_lookup(args.skill_name)

    if args.json:
        # JSON output for programmatic use
        import json
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        if result['found']:
            skill = result['skill']
            print(f"✓ Found: {skill['name']}")
            print(f"  Script: {skill['script']}")
            print(f"  Category: {skill.get('category', 'unknown')}")
            print(f"  Complexity: {skill.get('complexity', 'unknown')}")

            if skill.get('cli_enabled'):
                print(f"\n  CLI Enabled: Yes")
                print(f"  Format: {skill.get('cli_format', 'unknown')}")
                print(f"  Signature: {skill.get('cli_signature', 'N/A')}")
                print(f"  Example: {skill.get('cli_example', 'N/A')}")

            if result['healthy']:
                print(f"\n  Health: ✓ Healthy")
                print(f"  Status: Ready to execute")
            else:
                print(f"\n  Health: ✗ Broken")
                print(f"  Issues: {skill.get('health', {}).get('issues', [])}")
        else:
            print(f"✗ Skill '{args.skill_name}' not found in index")
            print(f"\nSuggestion: Use strategy.py to find similar skills or create new one")
