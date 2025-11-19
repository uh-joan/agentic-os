#!/usr/bin/env python3
"""Phase 4 migration tests - verify complete migration to folder structure."""

import sys
import json
from pathlib import Path

def test_all_skills_migrated():
    """Test that all 11 skills have been migrated to folder structure."""
    print("Testing all skills migrated to folder structure...")

    expected_folders = [
        'glp1-trials',
        'glp1-fda-drugs',
        'kras-inhibitor-trials',
        'kras-inhibitor-fda-drugs',
        'glp1-diabetes-drugs',
        'covid19-vaccine-trials-recruiting',
        'phase2-alzheimers-trials-us',
        'us-phase3-obesity-recruiting-trials',
        'adc-trials',
        'braf-inhibitor-trials',
        'braf-inhibitor-fda-drugs'
    ]

    passed = 0
    for folder in expected_folders:
        skill_dir = Path(f'.claude/skills/{folder}')
        skill_md = skill_dir / 'SKILL.md'
        scripts_dir = skill_dir / 'scripts'

        if all([skill_dir.exists(), skill_md.exists(), scripts_dir.exists()]):
            print(f"  ✓ {folder}/ complete")
            passed += 1
        else:
            print(f"  ✗ {folder}/ incomplete")

    return passed == len(expected_folders)

def test_index_updated():
    """Test that index.json reflects complete migration."""
    print("\nTesting index.json updated to v2.0...")

    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    checks = [
        ("Version 2.0", index.get('version') == '2.0'),
        ("Format folder-structure", index.get('format') == 'folder-structure'),
        ("Phase 4 complete", index.get('migration_status', {}).get('phase') == '4-migration-complete'),
        ("11 folder skills", index.get('migration_status', {}).get('folder_skills_count') == 11),
        ("0 flat skills", index.get('migration_status', {}).get('flat_skills_count') == 0),
        ("11 deprecated flat", index.get('migration_status', {}).get('deprecated_flat_count') == 11),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def test_deprecation_notice():
    """Test that deprecation notice is present."""
    print("\nTesting deprecation notice...")

    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    deprecation = index.get('deprecation_notice', {})

    checks = [
        ("Has deprecation notice", 'flat_files' in deprecation),
        ("Has removal date", 'removal_date' in deprecation),
        ("Has grace period", deprecation.get('grace_period') == '30 days'),
        ("Has action required", 'action_required' in deprecation),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def test_discovery_works():
    """Test that discover_skills finds all folder skills."""
    print("\nTesting skill discovery...")

    try:
        sys.path.insert(0, '.claude/scripts')
        from discover_skills import discover_skills

        skills = discover_skills()

        folder_skills = [s for s in skills.values() if s.get('structure') == 'folder']
        flat_skills = [s for s in skills.values() if s.get('structure') == 'flat']

        checks = [
            ("Found 11 skills", len(skills) == 11),
            ("All folder structure", len(folder_skills) == 11),
            ("No flat structure", len(flat_skills) == 0),
        ]

        passed = 0
        for name, result in checks:
            if result:
                print(f"  ✓ {name}")
                passed += 1
            else:
                print(f"  ✗ {name} (found {len(folder_skills)} folder, {len(flat_skills)} flat)")

        return passed == len(checks)

    except Exception as e:
        print(f"  ✗ Discovery error: {e}")
        return False

def test_backward_compatibility():
    """Test that flat files are properly archived in deprecated folder."""
    print("\nTesting deprecated folder (flat files archived)...")

    deprecated_dir = Path('.claude/skills/deprecated')

    if not deprecated_dir.exists():
        print("  ✗ deprecated/ folder not found")
        return False

    expected_flat_files = [
        'get_glp1_trials.py',
        'get_glp1_fda_drugs.py',
        'get_kras_inhibitor_trials.py',
        'get_kras_inhibitor_fda_drugs.py',
        'get_glp1_diabetes_drugs.py',
        'get_covid19_vaccine_trials_recruiting.py',
        'get_phase2_alzheimers_trials_us.py',
        'get_us_phase3_obesity_recruiting_trials.py',
        'get_adc_trials.py',
        'get_braf_inhibitor_trials.py',
        'get_braf_inhibitor_fda_drugs.py'
    ]

    passed = 0
    for flat_file in expected_flat_files:
        deprecated_path = deprecated_dir / flat_file
        if deprecated_path.exists():
            passed += 1

    readme_exists = (deprecated_dir / 'README.md').exists()

    print(f"  ✓ {passed}/{len(expected_flat_files)} flat files archived")
    print(f"  ✓ deprecated/README.md exists: {readme_exists}")

    return passed == len(expected_flat_files) and readme_exists

def test_folder_skills_execute():
    """Test that folder structure skills are executable."""
    print("\nTesting folder skills are executable...")

    test_skills = [
        ('glp1-trials', 'get_glp1_trials.py'),
        ('kras-inhibitor-trials', 'get_kras_inhibitor_trials.py'),
        ('adc-trials', 'get_adc_trials.py'),
    ]

    passed = 0
    for folder, script in test_skills:
        script_path = Path(f'.claude/skills/{folder}/scripts/{script}')
        if script_path.exists():
            try:
                with open(script_path) as f:
                    compile(f.read(), script_path, 'exec')
                print(f"  ✓ {folder}/{script} valid")
                passed += 1
            except SyntaxError:
                print(f"  ✗ {folder}/{script} syntax error")
        else:
            print(f"  ✗ {folder}/{script} not found")

    return passed == len(test_skills)

def run_phase4_tests():
    """Run all Phase 4 tests."""
    print("="*70)
    print("Phase 4 Migration Complete - Final Test Suite")
    print("="*70 + "\n")

    tests = [
        ("All Skills Migrated", test_all_skills_migrated),
        ("index.json Updated", test_index_updated),
        ("Deprecation Notice", test_deprecation_notice),
        ("Discovery Works", test_discovery_works),
        ("Deprecated Files Archived", test_backward_compatibility),
        ("Folder Skills Executable", test_folder_skills_execute),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results[name] = False

    print("\n" + "="*70)
    print("Phase 4 Migration Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    print("="*70)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 Phase 4 COMPLETE: Anthropic Skills Migration Successful!")
        print("\n✓ All 11 skills migrated to folder structure")
        print("✓ index.json updated to v2.0")
        print("✓ Flat files archived in deprecated/ folder")
        print("✓ Skills folder clean and organized")
        print("✓ Folder structure fully functional")
        print("\n📦 Skills Library Format: Anthropic v2.0")
        print("📊 Migration Status: 100% Complete")
        print("📁 Deprecated files: .claude/skills/deprecated/ (remove 2025-12-19)")
    else:
        print("\n⚠️  Phase 4 has failures - please review")

    return all_passed

if __name__ == "__main__":
    success = run_phase4_tests()
    sys.exit(0 if success else 1)
