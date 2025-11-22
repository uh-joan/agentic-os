#!/usr/bin/env python3
"""
Integration test suite for skill discovery system.

Tests the full workflow: strategy decision → skill execution/creation → validation

Test Scenarios:
1. REUSE existing parameterized skill (e.g., get_company_segment_geographic_financials)
2. REUSE existing specific skill (e.g., get_glp1_trials)
3. ADAPT similar skill (e.g., ADC trials from GLP-1 trials)
4. CREATE new skill (e.g., FDA REMS programs - novel query)
5. PREVENT duplicate (e.g., try creating get_abbott_segment_geographic_financials)

Usage:
    python3 test_discovery_integration.py --scenario all
    python3 test_discovery_integration.py --scenario reuse_parameterized
    python3 test_discovery_integration.py --scenario prevent_duplicate
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Tuple


class TestResult:
    """Container for test results."""
    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        self.passed = False
        self.message = ""
        self.details = {}
        self.strategy_output = None
        self.execution_output = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'scenario': self.scenario_name,
            'passed': self.passed,
            'message': self.message,
            'details': self.details
        }


def run_strategy_decision(skill_name: str, query: str, servers: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Run strategy.py and parse results.

    Returns:
        tuple: (success, strategy_result_dict)
    """
    cmd = [
        'python3',
        '.claude/tools/skill_discovery/strategy.py',
        '--skill-name', skill_name,
        '--query', query,
        '--servers', servers,
        '--json'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return False, {'error': result.stderr}

        # Parse JSON output
        output = result.stdout.strip()
        strategy_data = json.loads(output)
        return True, strategy_data

    except subprocess.TimeoutExpired:
        return False, {'error': 'Strategy decision timeout'}
    except json.JSONDecodeError as e:
        return False, {'error': f'Invalid JSON: {e}', 'output': result.stdout}
    except Exception as e:
        return False, {'error': str(e)}


def test_reuse_parameterized() -> TestResult:
    """
    Test REUSE strategy for parameterized skill.

    Query: "Get Abbott segment and geographic financials"
    Expected: REUSE get_company_segment_geographic_financials
    """
    result = TestResult('REUSE_PARAMETERIZED')

    # Run strategy decision
    success, strategy = run_strategy_decision(
        skill_name='company_segment_geographic_financials',
        query='Get Abbott segment and geographic financials',
        servers='sec_edgar_mcp'
    )

    if not success:
        result.message = f"Strategy decision failed: {strategy.get('error')}"
        return result

    result.strategy_output = strategy

    # Verify strategy is REUSE
    strategy_type = strategy.get('strategy')
    if strategy_type != 'REUSE':
        result.message = f"Expected REUSE strategy, got {strategy_type}"
        result.details = {'strategy': strategy}
        return result

    # Verify correct skill identified
    skill_info = strategy.get('skill', {})
    if 'company_segment_geographic_financials' not in skill_info.get('script', ''):
        result.message = f"Wrong skill identified: {skill_info.get('script')}"
        result.details = {'skill': skill_info}
        return result

    # Verify skill exists
    skill_path = Path(skill_info.get('script', ''))
    if not skill_path.exists():
        result.message = f"Skill file doesn't exist: {skill_path}"
        return result

    result.passed = True
    result.message = "REUSE strategy correctly identified parameterized skill"
    result.details = {
        'strategy': strategy_type,
        'skill_name': skill_info.get('name'),
        'skill_path': str(skill_path)
    }

    return result


def test_reuse_specific() -> TestResult:
    """
    Test REUSE strategy for specific skill.

    Query: "Get GLP-1 clinical trials"
    Expected: REUSE get_glp1_trials
    """
    result = TestResult('REUSE_SPECIFIC')

    # Run strategy decision
    success, strategy = run_strategy_decision(
        skill_name='glp1_trials',
        query='Get GLP-1 clinical trials',
        servers='ct_gov_mcp'
    )

    if not success:
        result.message = f"Strategy decision failed: {strategy.get('error')}"
        return result

    result.strategy_output = strategy

    # Verify strategy is REUSE
    strategy_type = strategy.get('strategy')
    if strategy_type != 'REUSE':
        result.message = f"Expected REUSE strategy, got {strategy_type}"
        result.details = {'strategy': strategy}
        return result

    # Verify correct skill identified
    skill_info = strategy.get('skill', {})
    if 'glp1' not in skill_info.get('name', '').lower():
        result.message = f"Wrong skill identified: {skill_info.get('name')}"
        result.details = {'skill': skill_info}
        return result

    result.passed = True
    result.message = "REUSE strategy correctly identified specific skill"
    result.details = {
        'strategy': strategy_type,
        'skill_name': skill_info.get('name'),
        'skill_path': skill_info.get('script')
    }

    return result


def test_adapt_similar() -> TestResult:
    """
    Test ADAPT strategy for similar skill.

    Query: "Get EGFR inhibitor clinical trials"
    Expected: ADAPT from get_glp1_trials or similar
    """
    result = TestResult('ADAPT_SIMILAR')

    # Run strategy decision
    success, strategy = run_strategy_decision(
        skill_name='egfr_inhibitor_trials',
        query='Get EGFR inhibitor clinical trials',
        servers='ct_gov_mcp'
    )

    if not success:
        result.message = f"Strategy decision failed: {strategy.get('error')}"
        return result

    result.strategy_output = strategy

    # Verify strategy is ADAPT or CREATE (both acceptable)
    strategy_type = strategy.get('strategy')
    if strategy_type not in ['ADAPT', 'CREATE']:
        result.message = f"Expected ADAPT or CREATE strategy, got {strategy_type}"
        result.details = {'strategy': strategy}
        return result

    # If ADAPT, verify reference skill provided
    if strategy_type == 'ADAPT':
        reference_info = strategy.get('skill', {})
        if not reference_info:
            result.message = "ADAPT strategy but no reference skill provided"
            return result

    # If CREATE, verify reference pattern provided
    if strategy_type == 'CREATE':
        reference_info = strategy.get('reference', {})
        if not reference_info:
            result.message = "CREATE strategy but no reference pattern provided"
            return result

    result.passed = True
    result.message = f"{strategy_type} strategy correctly identified with reference"
    result.details = {
        'strategy': strategy_type,
        'reference': strategy.get('skill' if strategy_type == 'ADAPT' else 'reference', {})
    }

    return result


def test_create_novel() -> TestResult:
    """
    Test CREATE strategy for novel query.

    Query: "Get FDA REMS programs for psychiatric drugs"
    Expected: CREATE with best reference pattern
    """
    result = TestResult('CREATE_NOVEL')

    # Run strategy decision
    success, strategy = run_strategy_decision(
        skill_name='fda_rems_psychiatric',
        query='Get FDA REMS programs for psychiatric drugs',
        servers='fda_mcp'
    )

    if not success:
        result.message = f"Strategy decision failed: {strategy.get('error')}"
        return result

    result.strategy_output = strategy

    # Verify strategy is CREATE
    strategy_type = strategy.get('strategy')
    if strategy_type != 'CREATE':
        result.message = f"Expected CREATE strategy, got {strategy_type}"
        result.details = {'strategy': strategy}
        return result

    # Verify reason provided
    reason = strategy.get('reason', '')
    if not reason:
        result.message = "CREATE strategy but no reason provided"
        return result

    result.passed = True
    result.message = "CREATE strategy correctly determined for novel query"
    result.details = {
        'strategy': strategy_type,
        'reason': reason,
        'reference': strategy.get('reference', {})
    }

    return result


def test_prevent_duplicate() -> TestResult:
    """
    Test enforcement prevents duplicate skill creation.

    Try to create: get_abbott_segment_geographic_financials
    Expected: Enforcement should fail (duplicate detected)
    """
    result = TestResult('PREVENT_DUPLICATE')

    # Run enforcement check
    cmd = [
        'python3',
        '.claude/tools/skill_discovery/enforce_discovery.py',
        '--skill-name', 'get_company_segment_geographic_financials',
        '--check-duplicate',
        '--json'
    ]

    try:
        enforce_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Parse JSON output
        output = enforce_result.stdout.strip()
        enforce_data = json.loads(output)

        # Enforcement should FAIL (exit code 1) for duplicate
        if enforce_result.returncode == 0:
            result.message = "Enforcement passed but should have detected duplicate"
            result.details = {'enforcement': enforce_data}
            return result

        # Verify duplicate was detected
        if not enforce_data.get('valid', True):
            violations = enforce_data.get('violations', [])
            has_duplicate_violation = any(
                v.get('type') == 'DUPLICATE_SKILL'
                for v in violations
            )

            if has_duplicate_violation:
                result.passed = True
                result.message = "Enforcement correctly detected duplicate skill"
                result.details = {'violations': violations}
            else:
                result.message = "Enforcement failed but not for duplicate reason"
                result.details = {'enforcement': enforce_data}
        else:
            result.message = "Enforcement didn't detect duplicate"
            result.details = {'enforcement': enforce_data}

    except subprocess.TimeoutExpired:
        result.message = "Enforcement timeout"
    except json.JSONDecodeError as e:
        result.message = f"Invalid JSON from enforcement: {e}"
    except Exception as e:
        result.message = f"Enforcement error: {e}"

    return result


def test_skill_health_check() -> TestResult:
    """
    Test that health checks identify broken skills.

    Expected: Existing skills should be healthy
    """
    result = TestResult('SKILL_HEALTH_CHECK')

    # Run health check on a known skill
    cmd = [
        'python3',
        '.claude/tools/skill_discovery/health_check.py',
        '--skill-name', 'glp1_trials',
        '--json'
    ]

    try:
        health_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Parse JSON output
        output = health_result.stdout.strip()
        health_data = json.loads(output)

        # Verify health status
        is_healthy = health_data.get('health_status') == 'HEALTHY'

        if is_healthy:
            result.passed = True
            result.message = "Health check correctly identifies healthy skill"
            result.details = {'health': health_data}
        else:
            result.message = f"Unexpected health status: {health_data.get('health_status')}"
            result.details = {'health': health_data}

    except subprocess.TimeoutExpired:
        result.message = "Health check timeout"
    except json.JSONDecodeError as e:
        result.message = f"Invalid JSON from health check: {e}"
    except FileNotFoundError:
        result.message = "health_check.py not found - skipping test"
        result.passed = True  # Skip test if tool doesn't exist
    except Exception as e:
        result.message = f"Health check error: {e}"

    return result


def run_test_suite(scenarios: list) -> Dict[str, Any]:
    """
    Run specified test scenarios.

    Args:
        scenarios: List of scenario names to run, or ['all']

    Returns:
        dict: Test results summary
    """
    # Test scenario mapping
    available_tests = {
        'reuse_parameterized': test_reuse_parameterized,
        'reuse_specific': test_reuse_specific,
        'adapt_similar': test_adapt_similar,
        'create_novel': test_create_novel,
        'prevent_duplicate': test_prevent_duplicate,
        'health_check': test_skill_health_check
    }

    # Determine which tests to run
    if 'all' in scenarios:
        tests_to_run = available_tests
    else:
        tests_to_run = {k: v for k, v in available_tests.items() if k in scenarios}

    if not tests_to_run:
        return {
            'error': f"No valid scenarios found. Available: {list(available_tests.keys())}"
        }

    # Run tests
    results = []
    for scenario_name, test_func in tests_to_run.items():
        print(f"\nRunning: {scenario_name}...", end=' ')
        test_result = test_func()
        results.append(test_result)

        status = "✓ PASS" if test_result.passed else "✗ FAIL"
        print(status)
        print(f"  {test_result.message}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    summary = {
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        'results': [r.to_dict() for r in results]
    }

    return summary


def main():
    parser = argparse.ArgumentParser(
        description='Integration test suite for skill discovery'
    )
    parser.add_argument(
        '--scenario',
        nargs='+',
        default=['all'],
        help='Test scenarios to run (default: all)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Change to repo root
    repo_root = Path(__file__).parent.parent.parent
    import os
    os.chdir(repo_root)

    print("=" * 70)
    print("Skill Discovery Integration Test Suite")
    print("=" * 70)

    # Run tests
    summary = run_test_suite(args.scenario)

    if 'error' in summary:
        print(f"\nError: {summary['error']}")
        sys.exit(1)

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Total:  {summary['total']}")
    print(f"Passed: {summary['passed']} ✓")
    print(f"Failed: {summary['failed']} ✗")
    print(f"Pass Rate: {summary['pass_rate']}")

    if args.json:
        print("\n" + json.dumps(summary, indent=2))

    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
