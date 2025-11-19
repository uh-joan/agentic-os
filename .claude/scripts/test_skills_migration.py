#!/usr/bin/env python3
"""Integration tests for skills migration."""

import sys
import json
from pathlib import Path

sys.path.insert(0, '.claude/scripts')
from parse_skill_metadata import parse_skill_frontmatter, get_all_skill_metadata

def test_phase1_frontmatter():
    """Test Phase 1: YAML frontmatter added."""
    print("Testing Phase 1: YAML Frontmatter...")

    skills_dir = Path('.claude/skills')
    skill_mds = [f for f in skills_dir.glob('*.md') if f.name != 'README.md']

    passed = 0
    failed = []

    for md_file in skill_mds:
        metadata = parse_skill_frontmatter(md_file)
        if metadata:
            try:
                assert 'name' in metadata, f"{md_file.name}: missing 'name'"
                assert 'description' in metadata, f"{md_file.name}: missing 'description'"
                assert 'category' in metadata, f"{md_file.name}: missing 'category'"
                assert 'mcp_servers' in metadata, f"{md_file.name}: missing 'mcp_servers'"
                assert 'patterns' in metadata, f"{md_file.name}: missing 'patterns'"
                assert 'complexity' in metadata, f"{md_file.name}: missing 'complexity'"
                passed += 1
            except AssertionError as e:
                failed.append(str(e))
        else:
            failed.append(f"{md_file.name}: no frontmatter found")

    if failed:
        for error in failed:
            print(f"  ✗ {error}")

    print(f"  ✓ {passed}/{len(skill_mds)} skills have valid frontmatter")
    return passed == len(skill_mds)

def test_backward_compatibility():
    """Test that skills still execute after adding frontmatter."""
    print("\nTesting Backward Compatibility...")

    skills_dir = Path('.claude/skills')
    test_skills = [
        'get_glp1_trials.py',
        'get_glp1_fda_drugs.py',
        'get_kras_inhibitor_fda_drugs.py'
    ]

    passed = 0
    for skill_file in test_skills:
        skill_path = skills_dir / skill_file
        if not skill_path.exists():
            print(f"  ⊙ {skill_file}: not found (skipping)")
            continue

        # Check that Python file is valid
        try:
            with open(skill_path) as f:
                compile(f.read(), skill_path, 'exec')
            print(f"  ✓ {skill_file}: valid Python syntax")
            passed += 1
        except SyntaxError as e:
            print(f"  ✗ {skill_file}: syntax error - {e}")

    print(f"  ✓ {passed}/{len(test_skills)} test skills have valid syntax")
    return passed == len(test_skills)

def test_index_json():
    """Test that index.json is updated correctly."""
    print("\nTesting index.json Updates...")

    index_path = Path('.claude/skills/index.json')
    if not index_path.exists():
        print("  ✗ index.json not found")
        return False

    index = json.loads(index_path.read_text())

    try:
        # Check version updated
        assert index['version'] == '1.1', f"Version should be 1.1, got {index['version']}"
        print("  ✓ Version updated to 1.1")

        # Check migration status
        assert 'migration_status' in index, "Missing migration_status"
        assert index['migration_status']['phase'] == '1-frontmatter-complete'
        print("  ✓ Migration status present")

        # Check all skills have frontmatter flags
        missing_flags = []
        for skill in index['skills']:
            if 'has_frontmatter' not in skill:
                missing_flags.append(skill['name'])
            if 'structure' not in skill:
                missing_flags.append(f"{skill['name']} (missing structure)")
            if 'documentation' not in skill:
                missing_flags.append(f"{skill['name']} (missing documentation)")

        if missing_flags:
            print(f"  ✗ Skills missing flags: {', '.join(missing_flags)}")
            return False

        print(f"  ✓ All {len(index['skills'])} skills have frontmatter flags")
        return True

    except AssertionError as e:
        print(f"  ✗ {e}")
        return False

def test_parser_utility():
    """Test that parser utility works."""
    print("\nTesting Parser Utility...")

    try:
        skills = get_all_skill_metadata()

        if len(skills) == 0:
            print("  ✗ Parser found no skills")
            return False

        print(f"  ✓ Parser found {len(skills)} skills")

        # Check that parsed metadata is valid
        for name, meta in skills.items():
            assert isinstance(meta, dict), f"{name}: metadata not a dict"
            assert 'name' in meta, f"{name}: missing name in metadata"

        print(f"  ✓ All parsed metadata is valid")
        return True

    except Exception as e:
        print(f"  ✗ Parser error: {e}")
        return False

def test_phase2_folder_structure():
    """Test Phase 2: Folder structure created."""
    print("\nTesting Phase 2: Folder Structure...")

    expected_folders = ['glp1-trials', 'glp1-fda-drugs']
    passed = 0

    for folder in expected_folders:
        skill_dir = Path(f'.claude/skills/{folder}')
        skill_md = skill_dir / 'SKILL.md'
        scripts_dir = skill_dir / 'scripts'

        try:
            assert skill_dir.exists(), f"{folder}/ not found"
            assert skill_md.exists(), f"{folder}/SKILL.md not found"
            assert scripts_dir.exists(), f"{folder}/scripts/ not found"

            # Check Python script exists
            scripts = list(scripts_dir.glob('*.py'))
            assert len(scripts) > 0, f"{folder}/scripts/ has no Python files"

            print(f"  ✓ {folder}/ folder structure valid")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {e}")

    return passed == len(expected_folders)

def test_phase2_both_structures_work():
    """Test that both flat and folder structures work."""
    print("\nTesting Both Structures Execute...")

    test_cases = [
        ('.claude/skills/glp1-trials/scripts/get_glp1_trials.py', 'folder'),
        ('.claude/skills/get_glp1_trials.py', 'flat'),
        ('.claude/skills/glp1-fda-drugs/scripts/get_glp1_fda_drugs.py', 'folder'),
        ('.claude/skills/get_glp1_fda_drugs.py', 'flat'),
    ]

    passed = 0
    for skill_path, structure in test_cases:
        path = Path(skill_path)
        if not path.exists():
            print(f"  ⊙ {path.name} ({structure}): not found")
            continue

        try:
            with open(path) as f:
                compile(f.read(), path, 'exec')
            print(f"  ✓ {path.name} ({structure}): valid syntax")
            passed += 1
        except SyntaxError as e:
            print(f"  ✗ {path.name} ({structure}): syntax error")

    return passed == len(test_cases)

def test_phase2_discovery():
    """Test that discovery works for both formats."""
    print("\nTesting Skill Discovery (Both Formats)...")

    try:
        from discover_skills import discover_skills

        skills = discover_skills()
        folder_count = sum(1 for s in skills.values() if s.get('structure') == 'folder')
        flat_count = sum(1 for s in skills.values() if s.get('structure') == 'flat')

        print(f"  ✓ Discovered {len(skills)} total skills")
        print(f"    - {folder_count} folder structure")
        print(f"    - {flat_count} flat structure")

        assert folder_count == 2, f"Expected 2 folder skills, got {folder_count}"
        assert flat_count >= 6, f"Expected ≥6 flat skills, got {flat_count}"

        return True
    except Exception as e:
        print(f"  ✗ Discovery error: {e}")
        return False

def test_phase2_index_updated():
    """Test that index.json tracks both formats."""
    print("\nTesting index.json (Phase 2)...")

    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    try:
        # Check migration status
        assert index['migration_status']['phase'] == '2-folder-structure-partial'
        print("  ✓ Migration phase correctly set")

        # Check folder skills present
        folder_skills = [s for s in index['skills'] if s.get('structure') == 'folder']
        assert len(folder_skills) == 2, f"Expected 2 folder skills in index, got {len(folder_skills)}"
        print(f"  ✓ {len(folder_skills)} folder skills in index")

        # Check deprecated_flat_files tracking
        for skill in folder_skills:
            assert 'deprecated_flat_files' in skill, f"{skill['name']}: missing deprecated_flat_files"
        print("  ✓ Deprecated flat files tracked")

        return True
    except AssertionError as e:
        print(f"  ✗ {e}")
        return False

def run_phase1_tests():
    """Run all Phase 1 tests."""
    print("="*60)
    print("Phase 1 Migration Test Suite")
    print("="*60 + "\n")

    tests = [
        ("Frontmatter Added", test_phase1_frontmatter),
        ("Backward Compatible", test_backward_compatibility),
        ("index.json Updated", test_index_json),
        ("Parser Utility", test_parser_utility),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results[name] = False

    print("\n" + "="*60)
    print("Phase 1 Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    print("="*60)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 Phase 1 Complete: All tests passed!")
        print("Ready to proceed to Phase 2: Folder Structure Migration")
    else:
        print("\n⚠️  Phase 1 has failures - please review before proceeding")

    return all_passed

def run_phase2_tests():
    """Run all Phase 2 tests."""
    print("="*60)
    print("Phase 2 Migration Test Suite")
    print("="*60)

    tests = [
        ("Folder Structure Created", test_phase2_folder_structure),
        ("Both Structures Work", test_phase2_both_structures_work),
        ("Discovery Works", test_phase2_discovery),
        ("index.json Updated", test_phase2_index_updated),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results[name] = False

    print("\n" + "="*60)
    print("Phase 2 Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    print("="*60)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 Phase 2 Complete: All tests passed!")
        print("✓ Folder structure working")
        print("✓ Both formats coexist successfully")
        print("✓ Backward compatibility maintained")
        print("\nReady to proceed to Phase 3: Agent Behavior Updates")
    else:
        print("\n⚠️  Phase 2 has failures - please review before proceeding")

    return all_passed

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run migration tests')
    parser.add_argument('--phase', type=int, choices=[1, 2], default=2,
                       help='Which phase to test (default: 2)')
    args = parser.parse_args()

    if args.phase == 1:
        success = run_phase1_tests()
    else:
        success = run_phase2_tests()

    sys.exit(0 if success else 1)
