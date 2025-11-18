"""Response Validation Utilities for MCP Testing

Provides validation functions to check MCP tool responses against expected structures.
"""

from typing import Dict, Any, List, Optional, Callable
import json


class ValidationResult:
    """Result of a validation check"""

    def __init__(self, passed: bool, message: str, details: Optional[Dict[str, Any]] = None):
        self.passed = passed
        self.message = message
        self.details = details or {}

    def __bool__(self):
        return self.passed

    def __repr__(self):
        status = "✅" if self.passed else "❌"
        return f"{status} {self.message}"


class ResponseValidator:
    """Validates MCP tool responses"""

    def __init__(self):
        self.validations = []

    def validate_structure(
        self,
        response: Dict[str, Any],
        required_fields: List[str],
        optional_fields: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate response has required fields

        Args:
            response: MCP tool response
            required_fields: Fields that must be present
            optional_fields: Fields that may be present

        Returns:
            ValidationResult
        """
        missing = [f for f in required_fields if f not in response]

        if missing:
            return ValidationResult(
                False,
                f"Missing required fields: {', '.join(missing)}",
                {'missing_fields': missing, 'response_keys': list(response.keys())}
            )

        return ValidationResult(
            True,
            "All required fields present",
            {'required_fields': required_fields, 'response_keys': list(response.keys())}
        )

    def validate_field_type(
        self,
        response: Dict[str, Any],
        field: str,
        expected_type: type
    ) -> ValidationResult:
        """
        Validate a field has the expected type

        Args:
            response: MCP tool response
            field: Field name (supports dot notation for nested fields)
            expected_type: Expected Python type

        Returns:
            ValidationResult
        """
        # Navigate nested fields (e.g., "data.results")
        value = response
        path_parts = field.split('.')

        try:
            for part in path_parts:
                value = value[part]
        except (KeyError, TypeError):
            return ValidationResult(
                False,
                f"Field '{field}' not found in response",
                {'field': field, 'response_keys': list(response.keys())}
            )

        if not isinstance(value, expected_type):
            return ValidationResult(
                False,
                f"Field '{field}' has type {type(value).__name__}, expected {expected_type.__name__}",
                {'field': field, 'actual_type': type(value).__name__, 'expected_type': expected_type.__name__}
            )

        return ValidationResult(
            True,
            f"Field '{field}' has correct type {expected_type.__name__}",
            {'field': field, 'type': expected_type.__name__}
        )

    def validate_non_empty(
        self,
        response: Dict[str, Any],
        field: str
    ) -> ValidationResult:
        """
        Validate a field is not empty (for lists, dicts, strings)

        Args:
            response: MCP tool response
            field: Field name

        Returns:
            ValidationResult
        """
        if field not in response:
            return ValidationResult(
                False,
                f"Field '{field}' not found",
                {'field': field}
            )

        value = response[field]

        if isinstance(value, (list, dict, str)) and len(value) == 0:
            return ValidationResult(
                False,
                f"Field '{field}' is empty",
                {'field': field, 'type': type(value).__name__}
            )

        return ValidationResult(
            True,
            f"Field '{field}' is not empty",
            {'field': field, 'length': len(value) if hasattr(value, '__len__') else None}
        )

    def validate_custom(
        self,
        response: Dict[str, Any],
        validator_fn: Callable[[Dict[str, Any]], bool],
        description: str
    ) -> ValidationResult:
        """
        Run custom validation function

        Args:
            response: MCP tool response
            validator_fn: Function that takes response and returns bool
            description: Description of what the validator checks

        Returns:
            ValidationResult
        """
        try:
            passed = validator_fn(response)
            return ValidationResult(
                passed,
                f"Custom validation '{description}': {'passed' if passed else 'failed'}",
                {'description': description}
            )
        except Exception as e:
            return ValidationResult(
                False,
                f"Custom validation '{description}' raised exception: {str(e)}",
                {'description': description, 'error': str(e)}
            )

    def validate_count_parameter_effect(
        self,
        response_with_count: Dict[str, Any],
        response_without_count: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate that count parameter reduces response size (FDA MCP specific)

        Args:
            response_with_count: Response with count parameter
            response_without_count: Response without count parameter

        Returns:
            ValidationResult
        """
        with_size = len(json.dumps(response_with_count))
        without_size = len(json.dumps(response_without_count))

        if with_size >= without_size:
            return ValidationResult(
                False,
                f"Count parameter did not reduce response size ({with_size} >= {without_size})",
                {'with_count_size': with_size, 'without_count_size': without_size}
            )

        reduction_pct = ((without_size - with_size) / without_size) * 100

        return ValidationResult(
            True,
            f"Count parameter reduced response size by {reduction_pct:.1f}% ({without_size} → {with_size})",
            {
                'with_count_size': with_size,
                'without_count_size': without_size,
                'reduction_bytes': without_size - with_size,
                'reduction_pct': reduction_pct
            }
        )

    def validate_pagination(
        self,
        response: Dict[str, Any],
        expected_page_size: int
    ) -> ValidationResult:
        """
        Validate pagination works correctly

        Args:
            response: MCP tool response
            expected_page_size: Expected number of results

        Returns:
            ValidationResult
        """
        # Works for most MCPs that return results in a 'data' or 'results' field
        results = None

        if 'data' in response:
            results = response['data']
        elif 'results' in response:
            results = response['results']
        elif 'studies' in response:  # CT.gov
            results = response['studies']
        elif 'articles' in response:  # PubMed
            results = response['articles']

        if results is None:
            return ValidationResult(
                False,
                "Could not find results array in response",
                {'response_keys': list(response.keys())}
            )

        if not isinstance(results, list):
            return ValidationResult(
                False,
                f"Results is not a list (type: {type(results).__name__})",
                {'results_type': type(results).__name__}
            )

        actual_size = len(results)

        if actual_size > expected_page_size:
            return ValidationResult(
                False,
                f"Got more results than expected ({actual_size} > {expected_page_size})",
                {'actual_size': actual_size, 'expected_size': expected_page_size}
            )

        return ValidationResult(
            True,
            f"Pagination working correctly ({actual_size} results, limit {expected_page_size})",
            {'actual_size': actual_size, 'expected_size': expected_page_size}
        )


def validate_response(
    response: Dict[str, Any],
    checks: List[Dict[str, Any]]
) -> List[ValidationResult]:
    """
    Run multiple validation checks on a response

    Args:
        response: MCP tool response
        checks: List of validation check specifications
               Each check is a dict with 'type' and type-specific parameters

    Returns:
        List of ValidationResult objects

    Example:
        checks = [
            {'type': 'structure', 'required_fields': ['data', 'meta']},
            {'type': 'field_type', 'field': 'data', 'expected_type': list},
            {'type': 'non_empty', 'field': 'data'}
        ]
        results = validate_response(response, checks)
    """
    validator = ResponseValidator()
    results = []

    for check in checks:
        check_type = check.get('type')

        if check_type == 'structure':
            result = validator.validate_structure(
                response,
                check.get('required_fields', []),
                check.get('optional_fields')
            )
        elif check_type == 'field_type':
            result = validator.validate_field_type(
                response,
                check['field'],
                check['expected_type']
            )
        elif check_type == 'non_empty':
            result = validator.validate_non_empty(
                response,
                check['field']
            )
        elif check_type == 'custom':
            result = validator.validate_custom(
                response,
                check['validator_fn'],
                check['description']
            )
        else:
            result = ValidationResult(
                False,
                f"Unknown validation check type: {check_type}",
                {'check_type': check_type}
            )

        results.append(result)

    return results


__all__ = ['ValidationResult', 'ResponseValidator', 'validate_response']
