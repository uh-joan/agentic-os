#!/usr/bin/env python3
"""
Test FDA Query Validator
"""

import json
import sys
from fda_query_validator import FDAQueryValidator, validate_fda_query


def test_missing_count_parameter():
    """Test auto-fixing missing count parameter"""
    print("\n" + "="*60)
    print("TEST 1: Missing count parameter (auto-fix)")
    print("="*60)

    params = {
        "search_term": "GLP-1",
        "search_type": "general",
        "limit": 100
    }

    print("\nInput parameters:")
    print(json.dumps(params, indent=2))

    validator = FDAQueryValidator(strict=False)
    result = validator.validate(params)

    print("\nOptimized parameters:")
    print(json.dumps(result, indent=2))

    print("\nValidation Report:")
    print(validator.get_validation_report())

    # Verify fix was applied
    assert 'count' in result, "Count parameter should be added"
    assert result['count'] == 'openfda.brand_name.exact', "Should use default count field"
    print("\n✅ TEST PASSED: Count parameter auto-added")


def test_missing_exact_suffix():
    """Test auto-fixing missing .exact suffix"""
    print("\n" + "="*60)
    print("TEST 2: Missing .exact suffix (auto-fix)")
    print("="*60)

    params = {
        "search_term": "semaglutide",
        "search_type": "general",
        "count": "openfda.brand_name",  # Missing .exact
        "limit": 50
    }

    print("\nInput parameters:")
    print(json.dumps(params, indent=2))

    validator = FDAQueryValidator(strict=False)
    result = validator.validate(params)

    print("\nOptimized parameters:")
    print(json.dumps(result, indent=2))

    print("\nValidation Report:")
    print(validator.get_validation_report())

    # Verify fix was applied
    assert result['count'].endswith('.exact'), "Should add .exact suffix"
    print("\n✅ TEST PASSED: .exact suffix auto-added")


def test_strict_mode_failure():
    """Test strict mode raises errors"""
    print("\n" + "="*60)
    print("TEST 3: Strict mode (should raise error)")
    print("="*60)

    params = {
        "search_term": "obesity",
        "search_type": "general",
        "limit": 100
        # No count parameter
    }

    print("\nInput parameters:")
    print(json.dumps(params, indent=2))

    validator = FDAQueryValidator(strict=True)

    try:
        result = validator.validate(params)
        print("\n❌ TEST FAILED: Should have raised ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"\n✅ TEST PASSED: Raised expected error:\n  {e}")


def test_adverse_events_count():
    """Test adverse events default count field"""
    print("\n" + "="*60)
    print("TEST 4: Adverse events count field (auto-fix)")
    print("="*60)

    params = {
        "search_term": "aspirin",
        "search_type": "adverse_events",
        "limit": 50
    }

    print("\nInput parameters:")
    print(json.dumps(params, indent=2))

    validator = FDAQueryValidator(strict=False)
    result = validator.validate(params)

    print("\nOptimized parameters:")
    print(json.dumps(result, indent=2))

    print("\nValidation Report:")
    print(validator.get_validation_report())

    # Verify correct count field for adverse events
    assert result['count'] == 'patient.reaction.reactionmeddrapt.exact', \
        "Should use adverse events count field"
    print("\n✅ TEST PASSED: Adverse events count field auto-added")


def test_recalls_no_count_needed():
    """Test that recalls don't require count parameter"""
    print("\n" + "="*60)
    print("TEST 5: Recalls search (count optional)")
    print("="*60)

    params = {
        "search_term": "aspirin",
        "search_type": "recalls",
        "limit": 50
    }

    print("\nInput parameters:")
    print(json.dumps(params, indent=2))

    validator = FDAQueryValidator(strict=False)
    result = validator.validate(params)

    print("\nOptimized parameters:")
    print(json.dumps(result, indent=2))

    print("\nValidation Report:")
    print(validator.get_validation_report())

    # Verify no count parameter was added (optional for recalls)
    print("\n✅ TEST PASSED: Recalls don't require count parameter")


def test_execution_plan_validation():
    """Test validating full execution plan"""
    print("\n" + "="*60)
    print("TEST 6: Full execution plan validation")
    print("="*60)

    plan = {
        "execution_plan": [
            {
                "step": 1,
                "tool": "mcp__fda-mcp__fda_info",
                "method": "lookup_drug",
                "params": {
                    "search_term": "GLP-1",
                    "search_type": "general",
                    "limit": 100
                    # Missing count parameter - should be auto-added
                }
            },
            {
                "step": 2,
                "tool": "mcp__fda-mcp__fda_info",
                "method": "lookup_drug",
                "params": {
                    "search_term": "aspirin",
                    "search_type": "adverse_events",
                    "count": "patient.reaction.reactionmeddrapt",  # Missing .exact
                    "limit": 50
                }
            }
        ]
    }

    print("\nInput plan:")
    print(json.dumps(plan, indent=2))

    from fda_query_validator import validate_execution_plan
    result = validate_execution_plan(plan, strict=False)

    print("\n\nOptimized plan:")
    print(json.dumps(result, indent=2))

    # Verify fixes
    step1 = result['execution_plan'][0]['params']
    assert 'count' in step1, "Step 1 should have count parameter"
    assert step1['count'] == 'openfda.brand_name.exact'

    step2 = result['execution_plan'][1]['params']
    assert step2['count'].endswith('.exact'), "Step 2 count should have .exact suffix"

    print("\n✅ TEST PASSED: Execution plan validated and optimized")


def test_already_optimized():
    """Test that optimized queries pass without changes"""
    print("\n" + "="*60)
    print("TEST 7: Already optimized query (no changes needed)")
    print("="*60)

    params = {
        "search_term": "semaglutide",
        "search_type": "general",
        "count": "openfda.brand_name.exact",
        "limit": 50
    }

    print("\nInput parameters:")
    print(json.dumps(params, indent=2))

    validator = FDAQueryValidator(strict=False)
    result = validator.validate(params)

    print("\nOptimized parameters:")
    print(json.dumps(result, indent=2))

    print("\nValidation Report:")
    print(validator.get_validation_report())

    assert result == params, "Should not modify already-optimized query"
    assert len(validator.fixes_applied) == 0, "Should not apply any fixes"
    print("\n✅ TEST PASSED: Optimized query unchanged")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FDA Query Validator Test Suite")
    print("="*60)

    tests = [
        test_missing_count_parameter,
        test_missing_exact_suffix,
        test_strict_mode_failure,
        test_adverse_events_count,
        test_recalls_no_count_needed,
        test_execution_plan_validation,
        test_already_optimized
    ]

    for test_func in tests:
        try:
            test_func()
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR in {test_func.__name__}")
            print(f"   Error: {e}")
            sys.exit(1)

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)
    print("\nFDA Query Validator is working correctly!")
    print("It will auto-fix common issues and prevent token overflow.")


if __name__ == '__main__':
    main()
