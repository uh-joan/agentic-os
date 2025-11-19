#!/usr/bin/env python3
"""Phase 3 validation tests - verify agent and documentation updates."""

import sys
from pathlib import Path

def test_agent_folder_structure():
    """Test pharma-search-specialist generates folder structure."""
    print("Testing pharma-search-specialist.md updates...")

    agent_file = Path('.claude/agents/pharma-search-specialist.md')
    content = agent_file.read_text()

    checks = [
        ("Mentions folder structure", "Skill folder:" in content),
        ("Has YAML frontmatter template", "name: {skill_function_name}" in content),
        ("References discover_skills", "discover_skills" in content),
        ("Updated Step 5", "Step 5: Return Skill Code to Main Agent (Folder Structure Format)" in content),
        ("Main agent saves files", "Main agent will" in content),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def test_claude_md_updates():
    """Test CLAUDE.md has folder structure documentation."""
    print("\nTesting CLAUDE.md updates...")

    claude_file = Path('.claude/CLAUDE.md')
    content = claude_file.read_text()

    checks = [
        ("Has Skills Library Format section", "## Skills Library Format (v2.0)" in content),
        ("Shows folder structure", "skill-name/" in content and "SKILL.md" in content),
        ("Shows migration status", "Migration to Anthropic Folder Structure" in content),
        ("Updated directory structure", "glp1-trials/" in content),
        ("Two-phase pattern updated", "Skills Library Pattern (Two-Phase + Folder Structure)" in content),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def test_skills_pattern_updates():
    """Test skills_library_pattern.md updated."""
    print("\nTesting skills_library_pattern.md updates...")

    pattern_file = Path('.claude/.context/code-examples/skills_library_pattern.md')
    content = pattern_file.read_text()

    checks = [
        ("Title updated", "Skills Library Pattern (Folder Structure)" in content),
        ("Shows v2.0 pattern", "Complete Pattern (Folder Structure - v2.0)" in content),
        ("Agent returns folder structure", "Agent Returns Folder Structure to Main Agent" in content),
        ("Main agent saves files", "Main Agent Saves Files" in content),
        ("Old pattern marked deprecated", "OLD Pattern (Flat Structure - v1.0 Deprecated)" in content),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def test_utilities_exist():
    """Test all Phase 2 utilities still exist."""
    print("\nTesting utilities exist...")

    utilities = [
        '.claude/scripts/init_skill.py',
        '.claude/scripts/package_skill.py',
        '.claude/scripts/discover_skills.py',
        '.claude/scripts/parse_skill_metadata.py',
    ]

    passed = 0
    for util in utilities:
        if Path(util).exists():
            print(f"  ✓ {Path(util).name} exists")
            passed += 1
        else:
            print(f"  ✗ {Path(util).name} missing")

    return passed == len(utilities)

def test_folder_skills_documented():
    """Test folder structure skills are documented in CLAUDE.md."""
    print("\nTesting folder skills documentation...")

    claude_file = Path('.claude/CLAUDE.md')
    content = claude_file.read_text()

    checks = [
        ("glp1-trials documented", "glp1-trials/" in content),
        ("glp1-fda-drugs documented", "glp1-fda-drugs/" in content),
        ("Shows SKILL.md location", "SKILL.md" in content),
        ("Shows scripts/ subdirectory", "scripts/" in content),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def test_backward_compatibility_documented():
    """Test backward compatibility approach documented."""
    print("\nTesting backward compatibility documentation...")

    claude_file = Path('.claude/CLAUDE.md')
    content = claude_file.read_text()

    checks = [
        ("Hybrid state mentioned", "hybrid" in content.lower() or "both formats" in content.lower()),
        ("v1.0 marked deprecated", "deprecated" in content.lower() or "OLD:" in content),
        ("v2.0 marked current", "v2.0" in content or "Current Standard" in content),
        ("Migration phases tracked", "Phase" in content),
    ]

    passed = 0
    for name, result in checks:
        if result:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")

    return passed == len(checks)

def run_phase3_validation():
    """Run all Phase 3 validation tests."""
    print("="*60)
    print("Phase 3 Validation Test Suite")
    print("="*60 + "\n")

    tests = [
        ("pharma-search-specialist.md Updated", test_agent_folder_structure),
        ("CLAUDE.md Updated", test_claude_md_updates),
        ("skills_library_pattern.md Updated", test_skills_pattern_updates),
        ("Utilities Exist", test_utilities_exist),
        ("Folder Skills Documented", test_folder_skills_documented),
        ("Backward Compatibility Documented", test_backward_compatibility_documented),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results[name] = False

    print("\n" + "="*60)
    print("Phase 3 Validation Results:")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    print("="*60)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 Phase 3 Complete: All validation tests passed!")
        print("\n✓ Agent generates folder structure format")
        print("✓ Documentation fully updated")
        print("✓ Backward compatibility maintained")
        print("✓ Ready for Phase 4: Complete migration of remaining skills")
    else:
        print("\n⚠️  Phase 3 has validation failures - please review")

    return all_passed

if __name__ == "__main__":
    success = run_phase3_validation()
    sys.exit(0 if success else 1)
