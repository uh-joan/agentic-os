#!/usr/bin/env python3
"""
Example Workflow - Demonstrates Testing Infrastructure

This example shows the complete workflow for testing and repairing skills.
Run this to see the testing system in action.

Usage:
    python3 .claude/tools/testing/example_workflow.py
"""

import json
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def run_test(skill_path: str) -> dict:
    """Run test on skill and return result"""
    result = subprocess.run(
        [
            'python3',
            '.claude/tools/testing/test_runner.py',
            skill_path,
            '--json'
        ],
        capture_output=True,
        text=True
    )

    return json.loads(result.stdout)


def run_orchestrator(skill_path: str, iteration: int = 1, max_iterations: int = 3) -> dict:
    """Run orchestrator and return result"""
    result = subprocess.run(
        [
            'python3',
            '.claude/tools/testing/test_orchestrator.py',
            skill_path,
            '--iteration', str(iteration),
            '--max-iterations', str(max_iterations),
            '--json'
        ],
        capture_output=True,
        text=True
    )

    return json.loads(result.stdout)


def example_test_single_skill():
    """Example 1: Test a single skill"""
    print_header("Example 1: Test a Single Skill")

    # Pick a skill to test
    skill_path = ".claude/skills/glp1-trials/scripts/get_glp1_trials.py"

    # Check if skill exists
    if not Path(skill_path).exists():
        print_warning(f"Skill not found: {skill_path}")
        print_info("Skipping this example")
        return

    print_info(f"Testing: {skill_path}")

    # Run test
    result = run_test(skill_path)

    # Display results
    print(f"\nTest Results:")
    print(f"  Overall Status: {result['overall_status'].upper()}")
    print(f"  Tests Passed: {result['passed_tests']}/{result['total_tests']}")

    for test in result['tests']:
        status_symbol = '✓' if test['status'] == 'passed' else '✗'
        print(f"  [{status_symbol}] {test['test_type']}: {test['message']}")

    if result['overall_status'] == 'passed':
        print_success("All tests passed!")
    else:
        print_error(f"{result['failed_tests']} test(s) failed")


def example_test_with_orchestration():
    """Example 2: Test with orchestration (repair instructions)"""
    print_header("Example 2: Test with Orchestration")

    # Pick a skill to test
    skill_path = ".claude/skills/glp1-trials/scripts/get_glp1_trials.py"

    # Check if skill exists
    if not Path(skill_path).exists():
        print_warning(f"Skill not found: {skill_path}")
        print_info("Skipping this example")
        return

    print_info(f"Testing: {skill_path}")

    # Run orchestrator
    result = run_orchestrator(skill_path)

    # Display results
    print(f"\nOrchestration Results:")
    print(f"  Overall Status: {result['test_report']['overall_status'].upper()}")
    print(f"  Tests Passed: {result['test_report']['passed_tests']}/{result['test_report']['total_tests']}")
    print(f"  Iteration: {result['iteration']}/{result['max_iterations']}")
    print(f"  Needs Repair: {result['needs_repair']}")

    if result['needs_repair']:
        print_warning(f"\nRepair needed: {len(result['repair_instructions'])} issue(s) detected")

        for i, instr in enumerate(result['repair_instructions'], 1):
            print(f"\n  Issue {i}: [{instr['severity'].upper()}] {instr['issue_type']}")
            print(f"  Description: {instr['description']}")
            print(f"  Suggested Fix: {instr['suggested_fix'][:100]}...")

        print_info("\nNext Step: Invoke pharma-search-specialist with repair prompt")
    else:
        print_success("Skill is healthy!")


def example_batch_test():
    """Example 3: Batch test all skills"""
    print_header("Example 3: Batch Test All Skills")

    print_info("Testing all skills in library...")

    # Run batch test
    result = subprocess.run(
        [
            'python3',
            '.claude/tools/testing/batch_test_skills.py',
            '--json'
        ],
        capture_output=True,
        text=True
    )

    summary = json.loads(result.stdout)

    # Display summary
    print(f"\nLibrary Health Summary:")
    print(f"  Total Skills: {summary['total_skills']}")
    print(f"  ✓ Healthy: {summary['healthy_skills']} ({summary['health_percentage']}%)")
    print(f"  ✗ Broken: {summary['broken_skills']}")
    print(f"  ○ Untested: {summary['untested_skills']}")

    if summary['health_percentage'] > 90:
        print_success("Library health: EXCELLENT")
    elif summary['health_percentage'] > 75:
        print_success("Library health: GOOD")
    else:
        print_warning("Library health: NEEDS ATTENTION")

    # Show broken skills
    if summary['broken_skills'] > 0:
        print(f"\nBroken Skills:")
        broken = [r for r in summary['test_results'] if r['status'] == 'failed']
        for skill in broken[:5]:
            print(f"  ✗ {skill['skill_name']}")
            if 'issues' in skill:
                for issue in skill['issues'][:2]:
                    print(f"    - {issue}")


def example_repair_workflow():
    """Example 4: Simulated repair workflow"""
    print_header("Example 4: Simulated Repair Workflow")

    print_info("This example demonstrates the repair loop workflow")
    print_info("(Simulation only - doesn't actually invoke agents)\n")

    # Simulated broken skill
    print("Step 1: Create skill")
    print("  → pharma-search-specialist creates skill code")
    print("  → Save to .claude/skills/example-skill/\n")

    print("Step 2: Test skill")
    print("  → Run test_orchestrator.py")
    print("  → Status: FAILED (3/5 tests passed)\n")

    print("Step 3: Analyze failures")
    print("  → Issue 1: [CRITICAL] import_error")
    print("  → Issue 2: [HIGH] execution_error")
    print("  → Issue 3: [MEDIUM] schema_validation_error\n")

    print("Step 4: Generate repair prompt")
    print("  → Create detailed prompt with:")
    print("    - Issue descriptions")
    print("    - Suggested fixes")
    print("    - Execution output")
    print("    - Error output\n")

    print("Step 5: Repair iteration 1")
    print("  → Invoke pharma-search-specialist with prompt")
    print("  → Save fixed code")
    print("  → Re-test")
    print("  → Status: FAILED (4/5 tests passed)\n")

    print("Step 6: Repair iteration 2")
    print("  → Invoke pharma-search-specialist again")
    print("  → Save fixed code")
    print("  → Re-test")
    print("  → Status: PASSED (5/5 tests passed)\n")

    print_success("Repair successful after 2 iterations!")

    print("\nStep 7: Finalize")
    print("  → Update skill index")
    print("  → Execute skill to get results")
    print("  → Return results to user\n")

    print_info("This is how Claude Code closes the agentic loop!")


def main():
    """Run all examples"""
    print(f"{Colors.BOLD}")
    print("="*60)
    print("Skill Testing Infrastructure - Example Workflow")
    print("="*60)
    print(f"{Colors.RESET}")

    print_info("This script demonstrates the testing infrastructure in action")
    print_info("Each example shows a different testing scenario\n")

    # Run examples
    try:
        example_test_single_skill()
        example_test_with_orchestration()
        example_batch_test()
        example_repair_workflow()

        print_header("Summary")
        print_success("All examples completed!")
        print_info("See README.md for full documentation")
        print_info("See QUICK_REFERENCE.md for command cheat sheet")
        print_info("See CLAUDE_CODE_INTEGRATION.md for integration patterns")

    except Exception as e:
        print_error(f"Example failed: {str(e)}")
        print_info("This is expected if skills haven't been created yet")


if __name__ == "__main__":
    main()
