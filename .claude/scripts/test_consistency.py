#!/usr/bin/env python3
"""Test consistency of documentation after folder structure migration."""

import re
from pathlib import Path

def test_no_flat_imports():
    """Test that no documentation contains old flat structure imports."""
    print("Testing for outdated flat structure imports...")

    # Pattern for old flat imports
    old_pattern = r'from \.claude\.skills\.get_\w+ import'

    files_to_check = [
        '.claude/CLAUDE.md',
        '.claude/.context/code-examples/ctgov_markdown_parsing.md',
        '.claude/.context/code-examples/fda_json_parsing.md',
        '.claude/.context/code-examples/skills_library_pattern.md',
        '.claude/skills/README.md',
    ]

    # Add all SKILL.md files
    skills_dir = Path('.claude/skills')
    for folder in skills_dir.iterdir():
        if folder.is_dir() and folder.name != 'deprecated' and folder.name != '__pycache__':
            skill_md = folder / 'SKILL.md'
            if skill_md.exists():
                files_to_check.append(str(skill_md))

    issues = []
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()
        matches = re.findall(old_pattern, content)

        if matches:
            issues.append(f"{file_path}: {len(matches)} old imports found")

    if issues:
        print("  ✗ Found old flat structure imports:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print(f"  ✓ No old flat imports found ({len(files_to_check)} files checked)")
        return True

def test_folder_structure_imports():
    """Test that documentation uses correct folder structure imports."""
    print("\nTesting for correct folder structure imports...")

    # Pattern for new folder imports
    new_pattern = r'from \.claude\.skills\.\w+\.scripts\.\w+ import'

    files_to_check = [
        ('.claude/CLAUDE.md', 1),  # (file, expected_count)
        ('.claude/.context/code-examples/ctgov_markdown_parsing.md', 1),
        ('.claude/.context/code-examples/fda_json_parsing.md', 1),
        ('.claude/.context/code-examples/skills_library_pattern.md', 3),  # Multiple examples
        ('.claude/skills/README.md', 2),
    ]

    # Add all SKILL.md files (each should have 1)
    skills_dir = Path('.claude/skills')
    for folder in skills_dir.iterdir():
        if folder.is_dir() and folder.name != 'deprecated' and folder.name != '__pycache__':
            skill_md = folder / 'SKILL.md'
            if skill_md.exists():
                files_to_check.append((str(skill_md), 1))

    passed = 0
    failed = []

    for file_path, expected_count in files_to_check:
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()
        matches = re.findall(new_pattern, content)
        actual_count = len(matches)

        if actual_count >= expected_count:
            passed += 1
        else:
            failed.append(f"{path.name}: expected ≥{expected_count}, found {actual_count}")

    if failed:
        print(f"  ⚠ Some files missing folder imports:")
        for fail in failed:
            print(f"    - {fail}")
        print(f"  ✓ {passed}/{len(files_to_check)} files have correct imports")
        return passed == len(files_to_check)
    else:
        print(f"  ✓ All {len(files_to_check)} files have folder structure imports")
        return True

def test_execution_paths():
    """Test that execution paths reference folder structure."""
    print("\nTesting execution path references...")

    # Pattern for old execution paths
    old_exec_pattern = r'python3 \.claude/skills/get_\w+\.py'

    # Pattern for new execution paths
    new_exec_pattern = r'python3 \.claude/skills/[\w-]+/scripts/\w+\.py'

    files_to_check = [
        '.claude/CLAUDE.md',
        '.claude/skills/README.md',
    ]

    old_paths_found = []
    new_paths_found = []

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()

        old_matches = re.findall(old_exec_pattern, content)
        new_matches = re.findall(new_exec_pattern, content)

        if old_matches:
            old_paths_found.append(f"{path.name}: {len(old_matches)} old paths")
        if new_matches:
            new_paths_found.append(f"{path.name}: {len(new_matches)} new paths")

    if old_paths_found:
        print("  ✗ Found old execution paths:")
        for found in old_paths_found:
            print(f"    - {found}")
        return False

    if new_paths_found:
        print(f"  ✓ Found {len(new_paths_found)} files with new execution paths")
        return True
    else:
        print("  ⊙ No execution paths found (might be intentional)")
        return True

def test_agent_references():
    """Test that agent documentation is consistent."""
    print("\nTesting agent documentation...")

    agent_file = Path('.claude/agents/pharma-search-specialist.md')
    content = agent_file.read_text()

    checks = [
        ("References folder structure", "Skill folder:" in content),
        ("Has YAML template", "name: {skill_function_name}" in content),
        ("References SKILL.md", "SKILL.md" in content),
        ("References scripts/", "scripts/" in content),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def run_consistency_tests():
    """Run all consistency tests."""
    print("="*70)
    print("Documentation Consistency Test Suite")
    print("="*70 + "\n")

    tests = [
        ("No Old Flat Imports", test_no_flat_imports),
        ("Folder Structure Imports", test_folder_structure_imports),
        ("Execution Paths", test_execution_paths),
        ("Agent Documentation", test_agent_references),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results[name] = False

    print("\n" + "="*70)
    print("Consistency Test Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    print("="*70)

    all_passed = all(results.values())
    if all_passed:
        print("\n✅ All documentation is consistent with folder structure!")
        print("\n✓ No old flat imports found")
        print("✓ All imports use folder structure")
        print("✓ Execution paths updated")
        print("✓ Agent documentation correct")
        print("\n📚 Ready to test with real queries")
    else:
        print("\n⚠️  Some consistency issues found - please review")

    return all_passed

if __name__ == "__main__":
    import sys
    success = run_consistency_tests()
    sys.exit(0 if success else 1)
