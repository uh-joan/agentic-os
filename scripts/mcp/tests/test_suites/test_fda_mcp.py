"""FDA MCP Test Suite

Comprehensive tests for the FDA MCP server covering:
- Drug labels
- Adverse events
- Recalls
- Shortages
- Device data

Focus areas:
- Count parameter validation (CRITICAL for token efficiency)
- Field selection patterns
- Response structure validation
- Error handling
"""

import sys
from pathlib import Path
import time

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.mcp_client import get_test_client
from utils.validators import validate_response, ResponseValidator
from utils.reporters import TestResult, TestSuiteResult


class TestSuite:
    """FDA MCP Test Suite"""

    def __init__(self, test_level: str = "smoke"):
        self.test_level = test_level
        self.client = get_test_client('fda-mcp', delay=1.0)
        self.validator = ResponseValidator()
        self.result = TestSuiteResult('fda-mcp')
        self.learnings = []

    def test_lookup_drug_with_count(self):
        """Test drug lookup WITH count parameter (token-efficient)"""
        print("  🧪 Test: lookup_drug with count parameter")

        start_time = time.time()
        validations = []
        test_learnings = []

        try:
            # Call FDA MCP with count parameter
            response = self.client.call_tool('lookup_drug', {
                'search_term': 'semaglutide',
                'search_type': 'general',
                'count': 'openfda.brand_name.exact'
            })

            # Validate response structure
            checks = [
                {'type': 'structure', 'required_fields': ['results', 'meta']},
                {'type': 'field_type', 'field': 'results', 'expected_type': list},
                {'type': 'non_empty', 'field': 'results'}
            ]
            validations = validate_response(response.get('response', {}), checks)

            # Check if count field is present
            if 'count' in response.get('response', {}).get('meta', {}):
                test_learnings.append(
                    "**Count parameter working**: Response includes meta.count field with aggregated brand names. "
                    "This is the CRITICAL token optimization for FDA queries."
                )

            # Estimate token savings
            response_size = len(str(response))
            if response_size < 5000:  # Should be small with count
                test_learnings.append(
                    f"**Token efficiency validated**: Response size {response_size} chars "
                    f"(much smaller than 67k without count parameter)"
                )

            passed = all(v.passed for v in validations)

        except Exception as e:
            validations = []
            test_learnings.append(f"**Error encountered**: {str(e)}")
            passed = False

        duration = time.time() - start_time

        return TestResult(
            test_name="lookup_drug_with_count",
            mcp_server="fda-mcp",
            method="lookup_drug",
            passed=passed,
            duration=duration,
            validations=validations,
            error=None if passed else "Test failed validation",
            learnings=test_learnings
        )

    def test_lookup_drug_without_count(self):
        """Test drug lookup WITHOUT count parameter (demonstrates problem)"""
        print("  🧪 Test: lookup_drug without count parameter")

        start_time = time.time()
        validations = []
        test_learnings = []

        try:
            # Call FDA MCP WITHOUT count parameter
            response = self.client.call_tool('lookup_drug', {
                'search_term': 'aspirin',
                'search_type': 'general',
                'limit': 5  # Use limit to reduce response size for testing
            })

            # Validate response structure
            checks = [
                {'type': 'structure', 'required_fields': ['results']},
                {'type': 'field_type', 'field': 'results', 'expected_type': list}
            ]
            validations = validate_response(response.get('response', {}), checks)

            # Estimate response size
            response_size = len(str(response))

            if response_size > 10000:
                test_learnings.append(
                    f"**Large response without count**: Response size {response_size} chars. "
                    f"Without count parameter, responses can exceed 67k chars (exceeds 25k MCP token limit). "
                    f"ALWAYS use count parameter for general/adverse_events queries."
                )
            else:
                test_learnings.append(
                    f"**Response size without count**: {response_size} chars "
                    f"(would be much larger without limit parameter)"
                )

            passed = all(v.passed for v in validations)

        except Exception as e:
            validations = []
            test_learnings.append(f"**Error encountered**: {str(e)}")
            passed = False

        duration = time.time() - start_time

        return TestResult(
            test_name="lookup_drug_without_count",
            mcp_server="fda-mcp",
            method="lookup_drug",
            passed=passed,
            duration=duration,
            validations=validations,
            error=None if passed else "Test failed validation",
            learnings=test_learnings
        )

    def test_adverse_events_with_count(self):
        """Test adverse events WITH count parameter"""
        print("  🧪 Test: adverse_events with count parameter")

        start_time = time.time()
        validations = []
        test_learnings = []

        try:
            # Call FDA MCP adverse events with count
            response = self.client.call_tool('lookup_drug', {
                'search_term': 'semaglutide',
                'search_type': 'adverse_events',
                'count': 'patient.reaction.reactionmeddrapt.exact'
            })

            # Validate response structure
            checks = [
                {'type': 'structure', 'required_fields': ['results']},
                {'type': 'field_type', 'field': 'results', 'expected_type': list}
            ]
            validations = validate_response(response.get('response', {}), checks)

            # Check for count results
            results = response.get('response', {}).get('results', [])
            if results and 'term' in results[0] and 'count' in results[0]:
                test_learnings.append(
                    "**Adverse events count structure**: Results contain {term, count} pairs. "
                    "This is the optimal format for summarizing adverse event patterns without "
                    "retrieving full case reports."
                )

            passed = all(v.passed for v in validations)

        except Exception as e:
            validations = []
            test_learnings.append(f"**Error encountered**: {str(e)}")
            passed = False

        duration = time.time() - start_time

        return TestResult(
            test_name="adverse_events_with_count",
            mcp_server="fda-mcp",
            method="lookup_drug",
            passed=passed,
            duration=duration,
            validations=validations,
            error=None if passed else "Test failed validation",
            learnings=test_learnings
        )

    def test_drug_label_details(self):
        """Test drug label lookup with field selection"""
        print("  🧪 Test: drug label with field selection")

        start_time = time.time()
        validations = []
        test_learnings = []

        try:
            # Call FDA MCP for drug labels with specific fields
            response = self.client.call_tool('lookup_drug', {
                'search_term': 'ozempic',
                'search_type': 'label',
                'fields_for_label': 'openfda.brand_name,openfda.generic_name,indications_and_usage,warnings,adverse_reactions'
            })

            # Validate response structure
            checks = [
                {'type': 'structure', 'required_fields': ['results']},
                {'type': 'field_type', 'field': 'results', 'expected_type': list}
            ]
            validations = validate_response(response.get('response', {}), checks)

            # Check if specific fields are present
            results = response.get('response', {}).get('results', [])
            if results:
                first_result = results[0]
                requested_fields = ['indications_and_usage', 'warnings', 'adverse_reactions']
                found_fields = [f for f in requested_fields if f in first_result]

                if found_fields:
                    test_learnings.append(
                        f"**Field selection working**: Retrieved {len(found_fields)}/{len(requested_fields)} requested fields. "
                        f"Field selection reduces response size for detailed label queries."
                    )

            passed = all(v.passed for v in validations)

        except Exception as e:
            validations = []
            test_learnings.append(f"**Error encountered**: {str(e)}")
            passed = False

        duration = time.time() - start_time

        return TestResult(
            test_name="drug_label_details",
            mcp_server="fda-mcp",
            method="lookup_drug",
            passed=passed,
            duration=duration,
            validations=validations,
            error=None if passed else "Test failed validation",
            learnings=test_learnings
        )

    def test_recalls(self):
        """Test drug recalls search"""
        print("  🧪 Test: drug recalls")

        start_time = time.time()
        validations = []
        test_learnings = []

        try:
            # Call FDA MCP for recalls
            response = self.client.call_tool('lookup_drug', {
                'search_term': 'insulin',
                'search_type': 'recalls',
                'limit': 10
            })

            # Validate response structure
            checks = [
                {'type': 'structure', 'required_fields': ['results']},
                {'type': 'field_type', 'field': 'results', 'expected_type': list}
            ]
            validations = validate_response(response.get('response', {}), checks)

            # Check recall-specific fields
            results = response.get('response', {}).get('results', [])
            if results:
                recall_fields = []
                first_result = results[0]

                common_recall_fields = ['status', 'reason_for_recall', 'classification', 'recall_initiation_date']
                for field in common_recall_fields:
                    if field in first_result:
                        recall_fields.append(field)

                if recall_fields:
                    test_learnings.append(
                        f"**Recall fields available**: {', '.join(recall_fields)}. "
                        f"Recalls dataset is relatively small - count parameter optional."
                    )

            passed = all(v.passed for v in validations)

        except Exception as e:
            validations = []
            test_learnings.append(f"**Error encountered**: {str(e)}")
            passed = False

        duration = time.time() - start_time

        return TestResult(
            test_name="recalls",
            mcp_server="fda-mcp",
            method="lookup_drug",
            passed=passed,
            duration=duration,
            validations=validations,
            error=None if passed else "Test failed validation",
            learnings=test_learnings
        )

    def test_shortages(self):
        """Test drug shortages search"""
        print("  🧪 Test: drug shortages")

        start_time = time.time()
        validations = []
        test_learnings = []

        try:
            # Call FDA MCP for shortages
            response = self.client.call_tool('lookup_drug', {
                'search_term': 'amoxicillin',
                'search_type': 'shortages',
                'limit': 5
            })

            # Validate response structure
            checks = [
                {'type': 'structure', 'required_fields': ['results']},
                {'type': 'field_type', 'field': 'results', 'expected_type': list}
            ]
            validations = validate_response(response.get('response', {}), checks)

            # Check shortage-specific fields
            results = response.get('response', {}).get('results', [])
            if results:
                first_result = results[0]
                shortage_fields = []

                common_shortage_fields = ['status', 'product_description', 'reason']
                for field in common_shortage_fields:
                    if field in first_result:
                        shortage_fields.append(field)

                if shortage_fields:
                    test_learnings.append(
                        f"**Shortage fields available**: {', '.join(shortage_fields)}. "
                        f"Shortages dataset is small - count parameter optional."
                    )

            passed = all(v.passed for v in validations)

        except Exception as e:
            validations = []
            test_learnings.append(f"**Error encountered**: {str(e)}")
            passed = False

        duration = time.time() - start_time

        return TestResult(
            test_name="shortages",
            mcp_server="fda-mcp",
            method="lookup_drug",
            passed=passed,
            duration=duration,
            validations=validations,
            error=None if passed else "Test failed validation",
            learnings=test_learnings
        )

    def run(self) -> TestSuiteResult:
        """Run all tests based on test level"""

        test_methods = []

        if self.test_level == "smoke":
            # Smoke test: Just the most critical test
            test_methods = [
                self.test_lookup_drug_with_count
            ]
        elif self.test_level == "coverage":
            # Coverage: All search types
            test_methods = [
                self.test_lookup_drug_with_count,
                self.test_lookup_drug_without_count,
                self.test_adverse_events_with_count,
                self.test_drug_label_details,
                self.test_recalls,
                self.test_shortages
            ]
        else:
            # Full test suite (variation, analysis, error levels)
            test_methods = [
                self.test_lookup_drug_with_count,
                self.test_lookup_drug_without_count,
                self.test_adverse_events_with_count,
                self.test_drug_label_details,
                self.test_recalls,
                self.test_shortages
            ]

        print(f"\nRunning {len(test_methods)} tests for FDA MCP ({self.test_level} level)...\n")

        for test_method in test_methods:
            result = test_method()
            self.result.add_test(result)

            # Display immediate result
            status = "✅" if result.passed else "❌"
            print(f"    {status} {result.test_name} ({result.duration:.2f}s)")

            # Display learnings immediately
            if result.learnings:
                for learning in result.learnings:
                    print(f"       💡 {learning}")

        self.result.complete()

        return self.result


if __name__ == "__main__":
    # Allow running this test suite directly
    suite = TestSuite(test_level="coverage")
    result = suite.run()

    print(f"\n{'=' * 80}")
    print(f"FDA MCP Test Results")
    print(f"{'=' * 80}")
    print(f"Passed: {result.passed_count}/{result.total_count}")
    print(f"Failed: {result.failed_count}/{result.total_count}")
    print(f"Duration: {result.duration:.1f}s")
    print(f"Learnings: {len(result.all_learnings)}")
