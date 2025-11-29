#!/usr/bin/env python3
"""
Skill Test Runner - Executes and validates individual skills

Runs comprehensive tests on skills including:
- Syntax validation (Python compiles)
- Import validation (dependencies available)
- Execution validation (runs without errors)
- Data validation (returns expected format and content)
- Schema validation (required fields present)
"""

import sys
import subprocess
import json
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TestStatus(Enum):
    """Test result status"""
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestType(Enum):
    """Types of tests to run"""
    SYNTAX = "syntax"
    IMPORT = "import"
    EXECUTION = "execution"
    DATA = "data"
    SCHEMA = "schema"


@dataclass
class TestResult:
    """Result of a single test"""
    test_type: str
    status: str
    message: str
    details: Optional[Dict] = None
    execution_time: Optional[float] = None


@dataclass
class SkillTestReport:
    """Complete test report for a skill"""
    skill_name: str
    skill_path: str
    overall_status: str
    tests: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    execution_output: Optional[str] = None
    error_output: Optional[str] = None


class SkillTestRunner:
    """Runs comprehensive tests on skills"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.skills_dir = self.project_root / ".claude" / "skills"

    def test_skill(self, skill_path: str, args: List[str] = None) -> SkillTestReport:
        """
        Run all tests on a skill

        Args:
            skill_path: Path to skill script (relative to project root)
            args: Optional arguments to pass to skill

        Returns:
            SkillTestReport with results
        """
        full_path = self.project_root / skill_path
        skill_name = self._extract_skill_name(skill_path)

        tests = []

        # Test 1: Syntax validation
        syntax_result = self._test_syntax(full_path)
        tests.append(syntax_result)

        if syntax_result.status != TestStatus.PASSED.value:
            # Stop testing if syntax fails
            return self._create_report(skill_name, str(full_path), tests)

        # Test 2: Import validation
        import_result = self._test_imports(full_path)
        tests.append(import_result)

        if import_result.status != TestStatus.PASSED.value:
            # Stop testing if imports fail
            return self._create_report(skill_name, str(full_path), tests)

        # Test 3: Execution validation
        execution_result = self._test_execution(full_path, args)
        tests.append(execution_result)

        if execution_result.status != TestStatus.PASSED.value:
            # Stop testing if execution fails
            report = self._create_report(skill_name, str(full_path), tests)
            report.execution_output = execution_result.details.get('stdout', '')
            report.error_output = execution_result.details.get('stderr', '')
            return report

        # Test 4: Data validation
        data_result = self._test_data(execution_result.details.get('stdout', ''))
        tests.append(data_result)

        # Test 5: Schema validation (if data validation passed)
        if data_result.status == TestStatus.PASSED.value:
            schema_result = self._test_schema(
                execution_result.details.get('stdout', ''),
                self._infer_skill_type(skill_name)
            )
            tests.append(schema_result)

        report = self._create_report(skill_name, str(full_path), tests)
        report.execution_output = execution_result.details.get('stdout', '')
        return report

    def _test_syntax(self, skill_path: Path) -> TestResult:
        """Test if Python file has valid syntax"""
        try:
            with open(skill_path, 'r') as f:
                code = f.read()

            ast.parse(code)

            return TestResult(
                test_type=TestType.SYNTAX.value,
                status=TestStatus.PASSED.value,
                message="Python syntax is valid"
            )
        except SyntaxError as e:
            return TestResult(
                test_type=TestType.SYNTAX.value,
                status=TestStatus.FAILED.value,
                message=f"Syntax error: {str(e)}",
                details={'line': e.lineno, 'error': str(e)}
            )
        except Exception as e:
            return TestResult(
                test_type=TestType.SYNTAX.value,
                status=TestStatus.ERROR.value,
                message=f"Error reading file: {str(e)}"
            )

    def _test_imports(self, skill_path: Path) -> TestResult:
        """Test if all imports are available"""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("test_module", skill_path)
            if spec is None or spec.loader is None:
                return TestResult(
                    test_type=TestType.IMPORT.value,
                    status=TestStatus.ERROR.value,
                    message="Could not load module spec"
                )

            module = importlib.util.module_from_spec(spec)

            # Add .claude to sys.path for MCP imports
            sys.path.insert(0, str(self.project_root / ".claude"))

            try:
                spec.loader.exec_module(module)
            finally:
                # Clean up sys.path
                if str(self.project_root / ".claude") in sys.path:
                    sys.path.remove(str(self.project_root / ".claude"))

            return TestResult(
                test_type=TestType.IMPORT.value,
                status=TestStatus.PASSED.value,
                message="All imports successful"
            )
        except ImportError as e:
            return TestResult(
                test_type=TestType.IMPORT.value,
                status=TestStatus.FAILED.value,
                message=f"Import failed: {str(e)}",
                details={'error': str(e)}
            )
        except Exception as e:
            return TestResult(
                test_type=TestType.IMPORT.value,
                status=TestStatus.ERROR.value,
                message=f"Error during import test: {str(e)}",
                details={'error': str(e)}
            )

    def _test_execution(self, skill_path: Path, args: List[str] = None) -> TestResult:
        """Test if skill executes without errors"""
        import time

        start_time = time.time()

        try:
            cmd = [
                'python3',
                str(skill_path)
            ]

            if args:
                cmd.extend(args)

            # Set PYTHONPATH to include .claude directory
            env = {
                'PYTHONPATH': f"{self.project_root / '.claude'}:$PYTHONPATH"
            }

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                env={**subprocess.os.environ, **env}
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                return TestResult(
                    test_type=TestType.EXECUTION.value,
                    status=TestStatus.PASSED.value,
                    message="Skill executed successfully",
                    details={
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    },
                    execution_time=execution_time
                )
            else:
                return TestResult(
                    test_type=TestType.EXECUTION.value,
                    status=TestStatus.FAILED.value,
                    message=f"Execution failed with exit code {result.returncode}",
                    details={
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    },
                    execution_time=execution_time
                )
        except subprocess.TimeoutExpired:
            return TestResult(
                test_type=TestType.EXECUTION.value,
                status=TestStatus.ERROR.value,
                message="Execution timeout (>60s)",
                execution_time=60.0
            )
        except Exception as e:
            return TestResult(
                test_type=TestType.EXECUTION.value,
                status=TestStatus.ERROR.value,
                message=f"Error during execution: {str(e)}",
                details={'error': str(e)}
            )

    def _test_data(self, output: str) -> TestResult:
        """Test if skill returned data"""
        if not output or output.strip() == "":
            return TestResult(
                test_type=TestType.DATA.value,
                status=TestStatus.FAILED.value,
                message="No data returned"
            )

        # Check for common "no results" patterns
        no_results_patterns = [
            "0 trials found",
            "0 drugs found",
            "0 patents found",
            "0 publications found",
            "No results",
            "Total: 0"
        ]

        for pattern in no_results_patterns:
            if pattern.lower() in output.lower():
                return TestResult(
                    test_type=TestType.DATA.value,
                    status=TestStatus.FAILED.value,
                    message="Query returned zero results",
                    details={'pattern_matched': pattern}
                )

        return TestResult(
            test_type=TestType.DATA.value,
            status=TestStatus.PASSED.value,
            message="Data returned successfully",
            details={'output_length': len(output)}
        )

    def _test_schema(self, output: str, skill_type: str) -> TestResult:
        """Test if output matches expected schema for skill type"""
        # Define expected patterns for different skill types
        schema_patterns = {
            'trials': ['NCT', 'Phase', 'Status', 'Sponsor'],
            'fda_drugs': ['Application', 'Product', 'Approval', 'Date'],
            'patents': ['Patent', 'Publication', 'Inventor', 'Assignee'],
            'publications': ['PMID', 'Title', 'Author', 'Journal'],
            'financial': ['Revenue', 'Symbol', 'Company', 'Price'],
            'generic': ['Total', 'found', 'Summary']
        }

        expected_patterns = schema_patterns.get(skill_type, schema_patterns['generic'])

        # Check if at least one expected pattern is present
        matched_patterns = [p for p in expected_patterns if p.lower() in output.lower()]

        if matched_patterns:
            return TestResult(
                test_type=TestType.SCHEMA.value,
                status=TestStatus.PASSED.value,
                message="Output schema matches expected format",
                details={'matched_patterns': matched_patterns}
            )
        else:
            return TestResult(
                test_type=TestType.SCHEMA.value,
                status=TestStatus.FAILED.value,
                message="Output schema does not match expected format",
                details={
                    'expected_patterns': expected_patterns,
                    'matched_patterns': matched_patterns
                }
            )

    def _infer_skill_type(self, skill_name: str) -> str:
        """Infer skill type from name"""
        if 'trial' in skill_name.lower():
            return 'trials'
        elif 'fda' in skill_name.lower() or 'drug' in skill_name.lower():
            return 'fda_drugs'
        elif 'patent' in skill_name.lower():
            return 'patents'
        elif 'publication' in skill_name.lower() or 'pubmed' in skill_name.lower():
            return 'publications'
        elif any(x in skill_name.lower() for x in ['revenue', 'financial', 'segment']):
            return 'financial'
        else:
            return 'generic'

    def _extract_skill_name(self, skill_path: str) -> str:
        """Extract skill name from path"""
        path = Path(skill_path)
        return path.stem

    def _create_report(self, skill_name: str, skill_path: str, tests: List[TestResult]) -> SkillTestReport:
        """Create test report from test results"""
        passed = sum(1 for t in tests if t.status == TestStatus.PASSED.value)
        failed = sum(1 for t in tests if t.status == TestStatus.FAILED.value)
        error = sum(1 for t in tests if t.status == TestStatus.ERROR.value)

        overall_status = TestStatus.PASSED.value
        if error > 0:
            overall_status = TestStatus.ERROR.value
        elif failed > 0:
            overall_status = TestStatus.FAILED.value

        return SkillTestReport(
            skill_name=skill_name,
            skill_path=skill_path,
            overall_status=overall_status,
            tests=tests,
            total_tests=len(tests),
            passed_tests=passed,
            failed_tests=failed,
            error_tests=error
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Test a skill')
    parser.add_argument('skill_path', help='Path to skill script (relative to project root)')
    parser.add_argument('--args', nargs='*', help='Arguments to pass to skill')
    parser.add_argument('--json', action='store_true', help='Output JSON format')

    args = parser.parse_args()

    runner = SkillTestRunner()
    report = runner.test_skill(args.skill_path, args.args)

    if args.json:
        # Convert to dict for JSON serialization
        report_dict = asdict(report)
        print(json.dumps(report_dict, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"Test Report: {report.skill_name}")
        print(f"{'='*60}")
        print(f"Path: {report.skill_path}")
        print(f"Overall Status: {report.overall_status.upper()}")
        print(f"Tests: {report.passed_tests}/{report.total_tests} passed")
        print(f"{'='*60}\n")

        for i, test in enumerate(report.tests, 1):
            status_symbol = {
                TestStatus.PASSED.value: '✓',
                TestStatus.FAILED.value: '✗',
                TestStatus.ERROR.value: '⚠',
                TestStatus.SKIPPED.value: '○'
            }.get(test.status, '?')

            print(f"{i}. [{status_symbol}] {test.test_type.upper()}: {test.message}")

            if test.execution_time:
                print(f"   Execution time: {test.execution_time:.2f}s")

            if test.details and test.status != TestStatus.PASSED.value:
                print(f"   Details: {json.dumps(test.details, indent=6)}")
            print()

        if report.execution_output:
            print(f"{'='*60}")
            print("Execution Output:")
            print(f"{'='*60}")
            print(report.execution_output)

        if report.error_output:
            print(f"{'='*60}")
            print("Error Output:")
            print(f"{'='*60}")
            print(report.error_output)

    # Exit with appropriate code
    sys.exit(0 if report.overall_status == TestStatus.PASSED.value else 1)


if __name__ == "__main__":
    main()
