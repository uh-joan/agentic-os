#!/usr/bin/env python3
"""
FDA Query Validator
Enforces token-efficient query patterns for FDA MCP tool calls.

CRITICAL: FDA queries without count parameter can return 67,000+ tokens,
exceeding the 25k MCP limit and causing query failures.

This validator ensures:
1. Count parameter is present for large queries
2. .exact suffix is used for count aggregations
3. Proper field selection is applied
"""

import json
import sys
from typing import Dict, List, Any


class FDAQueryValidator:
    """Validates and optimizes FDA MCP query parameters"""

    # Search types that REQUIRE count parameter
    COUNT_REQUIRED_TYPES = ['general', 'adverse_events']

    # Search types where count is optional (small datasets)
    COUNT_OPTIONAL_TYPES = ['recalls', 'shortages']

    # Default count fields by search type
    DEFAULT_COUNT_FIELDS = {
        'general': 'openfda.brand_name.exact',
        'adverse_events': 'patient.reaction.reactionmeddrapt.exact',
        'label': 'openfda.brand_name.exact'
    }

    # Recommended field selections (70-90% token reduction)
    RECOMMENDED_FIELDS = {
        'general': [
            'openfda.brand_name',
            'openfda.generic_name',
            'openfda.application_number',
            'products.marketing_status',
            'products.dosage_form',
            'products.route',
            'sponsor_name'
        ],
        'adverse_events': [
            'patient.reaction.reactionmeddrapt',
            'serious',
            'patient.drug.medicinalproduct',
            'receivedate'
        ],
        'label': [
            'openfda.brand_name',
            'openfda.generic_name',
            'indications_and_usage',
            'warnings',
            'dosage_and_administration'
        ]
    }

    def __init__(self, strict: bool = True):
        """
        Initialize validator

        Args:
            strict: If True, raises errors. If False, auto-fixes and warns.
        """
        self.strict = strict
        self.warnings: List[str] = []
        self.fixes_applied: List[str] = []

    def validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and optimize FDA query parameters

        Args:
            params: FDA query parameters

        Returns:
            Optimized parameters (possibly modified)

        Raises:
            ValueError: If strict=True and validation fails
        """
        self.warnings = []
        self.fixes_applied = []

        # Make a copy to avoid modifying original
        params = params.copy()

        # Extract key parameters
        search_type = params.get('search_type', 'general')
        limit = params.get('limit', 25)
        count = params.get('count')

        # Validation 1: Check if count parameter is needed
        if search_type in self.COUNT_REQUIRED_TYPES:
            if not count:
                if limit > 10:  # Large query without count = disaster
                    msg = (
                        f"FDA {search_type} query with limit={limit} MUST include count parameter. "
                        f"Without it, query may return 67,000+ tokens and FAIL (exceeds 25k MCP limit)."
                    )

                    if self.strict:
                        raise ValueError(msg)
                    else:
                        # Auto-fix: Add default count parameter
                        default_count = self.DEFAULT_COUNT_FIELDS.get(search_type)
                        params['count'] = default_count
                        fix_msg = f"Auto-added count parameter: '{default_count}'"
                        self.fixes_applied.append(fix_msg)
                        self.warnings.append(f"{msg}\n  FIX: {fix_msg}")

        # Validation 2: Check .exact suffix on count parameter
        if count and not count.endswith('.exact'):
            msg = (
                f"Count parameter '{count}' should use .exact suffix for proper aggregation. "
                f"Recommended: '{count}.exact'"
            )

            if self.strict:
                raise ValueError(msg)
            else:
                # Auto-fix: Add .exact suffix
                params['count'] = f"{count}.exact"
                fix_msg = f"Added .exact suffix: '{params['count']}'"
                self.fixes_applied.append(fix_msg)
                self.warnings.append(f"{msg}\n  FIX: {fix_msg}")

        # Validation 3: Check field selection for detail queries
        if not count and limit > 50:  # Detail query without field selection
            search_type_key = search_type if search_type in self.RECOMMENDED_FIELDS else 'general'
            fields_param = f"fields_for_{search_type}"

            if fields_param not in params:
                recommended = ','.join(self.RECOMMENDED_FIELDS[search_type_key])
                msg = (
                    f"Large detail query (limit={limit}) without field selection may return excessive tokens. "
                    f"Recommended: Add '{fields_param}': '{recommended}'"
                )
                self.warnings.append(msg)

        # Validation 4: Warn about very large limits with count
        if count and limit > 100:
            msg = (
                f"Count query with limit={limit} is unnecessarily high. "
                f"Count queries return aggregated data, so limit=50 is usually sufficient."
            )
            self.warnings.append(msg)

        return params

    def get_validation_report(self) -> str:
        """Get human-readable validation report"""
        report = []

        if self.fixes_applied:
            report.append("🔧 AUTO-FIXES APPLIED:")
            for fix in self.fixes_applied:
                report.append(f"  ✓ {fix}")

        if self.warnings:
            report.append("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                report.append(f"  • {warning}")

        if not self.fixes_applied and not self.warnings:
            report.append("✅ Query parameters are optimized")

        return '\n'.join(report)


def validate_fda_query(params: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
    """
    Convenience function to validate FDA query parameters

    Args:
        params: FDA query parameters
        strict: If True, raises errors. If False, auto-fixes.

    Returns:
        Optimized parameters
    """
    validator = FDAQueryValidator(strict=strict)
    optimized_params = validator.validate(params)

    # Print report to stderr (won't interfere with JSON output)
    report = validator.get_validation_report()
    if report:
        print(report, file=sys.stderr)

    return optimized_params


def validate_execution_plan(plan: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
    """
    Validate all FDA queries in an execution plan

    Args:
        plan: Execution plan from pharma-search-specialist
        strict: If True, raises errors. If False, auto-fixes.

    Returns:
        Optimized execution plan
    """
    if 'execution_plan' not in plan:
        return plan

    plan = plan.copy()
    plan['execution_plan'] = plan['execution_plan'].copy()

    for i, step in enumerate(plan['execution_plan']):
        if step.get('tool') == 'mcp__fda-mcp__fda_info':
            print(f"\n📋 Validating Step {step.get('step', i+1)}...", file=sys.stderr)
            step['params'] = validate_fda_query(step['params'], strict=strict)

    return plan


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python fda_query_validator.py <execution_plan.json> [--strict]")
        print("\nValidates and optimizes FDA query parameters in execution plans.")
        print("Default mode: Auto-fix issues and warn")
        print("Strict mode: Raise errors on validation failures")
        sys.exit(1)

    plan_file = sys.argv[1]
    strict = '--strict' in sys.argv

    # Load execution plan
    with open(plan_file, 'r') as f:
        plan = json.load(f)

    print(f"🔍 Validating FDA queries in {plan_file}...\n", file=sys.stderr)

    try:
        optimized_plan = validate_execution_plan(plan, strict=strict)

        # Print optimized plan to stdout
        print(json.dumps(optimized_plan, indent=2))

        print("\n✅ Validation complete!", file=sys.stderr)

    except ValueError as e:
        print(f"\n❌ VALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
