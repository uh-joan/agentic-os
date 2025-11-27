#!/usr/bin/env python3
"""Audit skills for hardcoded __main__ blocks that should accept CLI arguments."""

import os
import re
import ast
from pathlib import Path

def extract_function_signature(filepath):
    """Extract main function name and parameters."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Find functions with parameters (excluding self)
                params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                if params:
                    return node.name, params
        return None, []
    except:
        return None, []

def check_main_block(filepath):
    """Check if __main__ block uses sys.argv or hardcoded values."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Find __main__ block
        if 'if __name__ == "__main__":' not in content:
            return None

        # Extract __main__ block
        main_start = content.find('if __name__ == "__main__":')
        main_block = content[main_start:]

        # Check if it uses sys.argv or argparse
        uses_cli = 'sys.argv' in main_block or 'argparse' in main_block or 'ArgumentParser' in main_block

        return {
            'has_main': True,
            'uses_cli': uses_cli,
            'main_block_preview': main_block[:300]
        }
    except:
        return None

def audit_skills():
    """Audit all skills in .claude/skills/."""
    skills_dir = Path('.claude/skills')
    issues = []

    for skill_folder in sorted(skills_dir.iterdir()):
        if not skill_folder.is_dir() or skill_folder.name.startswith('.'):
            continue

        # Check scripts folder
        scripts_dir = skill_folder / 'scripts'
        if not scripts_dir.exists():
            continue

        for script_file in scripts_dir.glob('*.py'):
            if script_file.name.startswith('__'):
                continue

            func_name, params = extract_function_signature(script_file)
            main_info = check_main_block(script_file)

            # Flag if:
            # 1. Function has parameters
            # 2. Has __main__ block
            # 3. Doesn't use CLI arguments
            if params and main_info and main_info['has_main'] and not main_info['uses_cli']:
                issues.append({
                    'skill': skill_folder.name,
                    'script': script_file.name,
                    'function': func_name,
                    'params': params,
                    'path': str(script_file)
                })

    return issues

if __name__ == "__main__":
    print("Auditing skills for hardcoded __main__ blocks...\n")

    issues = audit_skills()

    if not issues:
        print("✅ All skills with parameters use CLI arguments properly!")
    else:
        print(f"⚠️  Found {len(issues)} skill(s) with hardcoded __main__ blocks:\n")

        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue['skill']}")
            print(f"   Function: {issue['function']}({', '.join(issue['params'])})")
            print(f"   Path: {issue['path']}")
            print()
