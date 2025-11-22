#!/usr/bin/env python3
"""
Enforcement script to validate skill discovery workflow compliance.

Prevents duplicate skill creation by verifying that:
1. Strategy decision was run before skill creation
2. Strategy logic was followed (REUSE/ADAPT/CREATE)
3. No duplicate skill names in index
4. Workflow compliance

Usage:
    python3 enforce_discovery.py --skill-name {name} --agent-output "{output}"
    python3 enforce_discovery.py --skill-name {name} --check-duplicate
"""

import argparse
import json
import re
import sys
from pathlib import Path


def load_skills_index():
    """Load the skills index."""
    index_path = Path(".claude/skills/index.json")
    if not index_path.exists():
        return {}

    with open(index_path) as f:
        return json.load(f)


def check_duplicate_skill(skill_name):
    """
    Check if skill name already exists in index.

    Returns:
        tuple: (is_duplicate, existing_skill_info)
    """
    index = load_skills_index()

    for skill in index.get('skills', []):
        if skill.get('name') == skill_name:
            return True, skill

    return False, None


def validate_strategy_in_output(agent_output):
    """
    Check if strategy decision appears in agent output.

    Returns:
        tuple: (found_strategy, strategy_type, details)
    """
    # Look for strategy.py execution
    strategy_exec_pattern = r'python3.*?strategy\.py'
    has_strategy_exec = bool(re.search(strategy_exec_pattern, agent_output, re.IGNORECASE))

    # Look for strategy mentions (REUSE/ADAPT/CREATE)
    strategy_mentions = {
        'REUSE': bool(re.search(r'\bREUSE\b', agent_output, re.IGNORECASE)),
        'ADAPT': bool(re.search(r'\bADAPT\b', agent_output, re.IGNORECASE)),
        'CREATE': bool(re.search(r'\bCREATE\b', agent_output, re.IGNORECASE))
    }

    # Determine which strategy was used
    strategy_type = None
    for strat, found in strategy_mentions.items():
        if found:
            strategy_type = strat
            break

    return has_strategy_exec or any(strategy_mentions.values()), strategy_type, {
        'strategy_exec': has_strategy_exec,
        'mentions': strategy_mentions
    }


def validate_reuse_not_violated(agent_output, skill_name):
    """
    Check if REUSE strategy was violated (new skill created when should reuse).

    Returns:
        tuple: (is_valid, violation_message)
    """
    # Check if output mentions REUSE
    has_reuse = re.search(r'\bREUSE\b', agent_output, re.IGNORECASE)

    if not has_reuse:
        return True, None  # Not a REUSE case

    # Check if new skill code was generated despite REUSE
    # Look for indicators of new code generation
    new_code_indicators = [
        r'def\s+get_\w+\(',  # New function definition
        r'Skill folder:',     # Skill folder structure
        r'Complete SKILL\.md',  # Documentation generation
    ]

    has_new_code = any(re.search(pattern, agent_output, re.IGNORECASE)
                       for pattern in new_code_indicators)

    if has_new_code:
        return False, (
            f"VIOLATION: Strategy returned REUSE but agent generated new skill code. "
            f"Skill '{skill_name}' should have been executed, not recreated."
        )

    return True, None


def validate_skill_creation(skill_name, agent_output=None, check_duplicate_only=False):
    """
    Main validation function.

    Args:
        skill_name: Name of skill being created
        agent_output: Full agent response text
        check_duplicate_only: Only check for duplicates, skip other validations

    Returns:
        dict: Validation results
    """
    results = {
        'skill_name': skill_name,
        'valid': True,
        'violations': [],
        'warnings': [],
        'checks': {}
    }

    # Check 1: Duplicate skill name
    is_duplicate, existing_skill = check_duplicate_skill(skill_name)
    results['checks']['duplicate'] = {
        'passed': not is_duplicate,
        'existing_skill': existing_skill
    }

    if is_duplicate:
        results['valid'] = False
        results['violations'].append({
            'type': 'DUPLICATE_SKILL',
            'message': f"Skill '{skill_name}' already exists in index",
            'existing_skill': existing_skill,
            'suggestion': (
                f"Use existing skill at {existing_skill.get('script', 'N/A')} or "
                f"run strategy.py to determine if REUSE/ADAPT is appropriate"
            )
        })

    if check_duplicate_only:
        return results

    # Require agent output for further checks
    if not agent_output:
        results['warnings'].append({
            'type': 'NO_AGENT_OUTPUT',
            'message': 'Agent output not provided - cannot validate workflow'
        })
        return results

    # Check 2: Strategy decision present
    found_strategy, strategy_type, strategy_details = validate_strategy_in_output(agent_output)
    results['checks']['strategy_decision'] = {
        'passed': found_strategy,
        'strategy_type': strategy_type,
        'details': strategy_details
    }

    if not found_strategy:
        results['valid'] = False
        results['violations'].append({
            'type': 'MISSING_STRATEGY',
            'message': 'No evidence of strategy.py execution found in agent output',
            'suggestion': (
                'Agent must run strategy.py before creating new skills. '
                'Add Step 0 strategy decision to workflow.'
            )
        })

    # Check 3: REUSE strategy not violated
    reuse_valid, reuse_violation = validate_reuse_not_violated(agent_output, skill_name)
    results['checks']['reuse_compliance'] = {
        'passed': reuse_valid,
        'violation': reuse_violation
    }

    if not reuse_valid:
        results['valid'] = False
        results['violations'].append({
            'type': 'REUSE_VIOLATION',
            'message': reuse_violation,
            'suggestion': (
                'When strategy returns REUSE, execute existing skill instead of '
                'generating new code. Do not create duplicate skills.'
            )
        })

    # Check 4: Strategy type alignment
    if found_strategy and strategy_type and not is_duplicate:
        if strategy_type == 'REUSE':
            # REUSE but no existing skill found - potential issue
            results['warnings'].append({
                'type': 'STRATEGY_MISMATCH',
                'message': f"Strategy type is REUSE but skill '{skill_name}' not in index",
                'suggestion': 'Verify strategy.py output matches index state'
            })

    return results


def print_results(results, format='text'):
    """Print validation results."""
    if format == 'json':
        print(json.dumps(results, indent=2))
        return

    # Text format
    skill_name = results['skill_name']

    if results['valid']:
        print(f"✓ Validation PASSED for skill '{skill_name}'")
        print("\nAll checks passed:")
        for check_name, check_data in results['checks'].items():
            status = "✓" if check_data['passed'] else "✗"
            print(f"  {status} {check_name}")
    else:
        print(f"✗ Validation FAILED for skill '{skill_name}'")
        print(f"\n{len(results['violations'])} violation(s) found:\n")

        for i, violation in enumerate(results['violations'], 1):
            print(f"{i}. {violation['type']}: {violation['message']}")
            if 'suggestion' in violation:
                print(f"   Suggestion: {violation['suggestion']}")
            print()

    if results['warnings']:
        print(f"\n{len(results['warnings'])} warning(s):")
        for warning in results['warnings']:
            print(f"  ⚠ {warning['type']}: {warning['message']}")


def main():
    parser = argparse.ArgumentParser(
        description='Enforce skill discovery workflow compliance'
    )
    parser.add_argument(
        '--skill-name',
        required=True,
        help='Name of skill being validated'
    )
    parser.add_argument(
        '--agent-output',
        help='Full agent response text for workflow validation'
    )
    parser.add_argument(
        '--check-duplicate',
        action='store_true',
        help='Only check for duplicate skill names'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Run validation
    results = validate_skill_creation(
        skill_name=args.skill_name,
        agent_output=args.agent_output,
        check_duplicate_only=args.check_duplicate
    )

    # Print results
    print_results(results, format='json' if args.json else 'text')

    # Exit with appropriate code
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()
