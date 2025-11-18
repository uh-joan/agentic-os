"""Test Result Reporting Utilities

Generates test reports in multiple formats (Markdown, JSON).
"""

from typing import Dict, Any, List
import json
from datetime import datetime
from pathlib import Path


class TestResult:
    """Single test result"""

    def __init__(
        self,
        test_name: str,
        mcp_server: str,
        method: str,
        passed: bool,
        duration: float,
        validations: List[Any],
        error: str = None,
        learnings: List[str] = None
    ):
        self.test_name = test_name
        self.mcp_server = mcp_server
        self.method = method
        self.passed = passed
        self.duration = duration
        self.validations = validations
        self.error = error
        self.learnings = learnings or []
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'test_name': self.test_name,
            'mcp_server': self.mcp_server,
            'method': self.method,
            'passed': self.passed,
            'duration': self.duration,
            'validations': [
                {
                    'passed': v.passed,
                    'message': v.message,
                    'details': v.details
                } for v in self.validations
            ],
            'error': self.error,
            'learnings': self.learnings,
            'timestamp': self.timestamp
        }


class TestSuiteResult:
    """Results for a full test suite (one MCP server)"""

    def __init__(self, mcp_server: str):
        self.mcp_server = mcp_server
        self.tests: List[TestResult] = []
        self.start_time = datetime.now()
        self.end_time = None

    def add_test(self, test: TestResult):
        """Add a test result"""
        self.tests.append(test)

    def complete(self):
        """Mark suite as complete"""
        self.end_time = datetime.now()

    @property
    def duration(self) -> float:
        """Total duration in seconds"""
        if self.end_time is None:
            return 0
        return (self.end_time - self.start_time).total_seconds()

    @property
    def passed_count(self) -> int:
        """Number of passed tests"""
        return sum(1 for t in self.tests if t.passed)

    @property
    def failed_count(self) -> int:
        """Number of failed tests"""
        return sum(1 for t in self.tests if not t.passed)

    @property
    def total_count(self) -> int:
        """Total number of tests"""
        return len(self.tests)

    @property
    def all_learnings(self) -> List[str]:
        """All learnings from this suite"""
        learnings = []
        for test in self.tests:
            learnings.extend(test.learnings)
        return learnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'mcp_server': self.mcp_server,
            'total_tests': self.total_count,
            'passed': self.passed_count,
            'failed': self.failed_count,
            'duration': self.duration,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'tests': [t.to_dict() for t in self.tests],
            'learnings': self.all_learnings
        }


class TestReporter:
    """Generate test reports"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_summary_md(self, suites: List[TestSuiteResult]) -> str:
        """Generate summary markdown report"""

        total_tests = sum(s.total_count for s in suites)
        total_passed = sum(s.passed_count for s in suites)
        total_failed = sum(s.failed_count for s in suites)
        total_learnings = sum(len(s.all_learnings) for s in suites)

        lines = [
            f"# MCP Test Results - {self.timestamp}",
            "",
            "## Overall Status",
            f"- ✅ Passed: {total_passed}/{total_tests} tests",
            f"- ❌ Failed: {total_failed}/{total_tests} tests",
            f"- 💡 Learnings: {total_learnings} total",
            "",
            "## By MCP Server",
            "| MCP | Tests | Passed | Failed | Learnings | Duration |",
            "|-----|-------|--------|--------|-----------|----------|"
        ]

        for suite in suites:
            status = "✅" if suite.failed_count == 0 else "⚠️"
            lines.append(
                f"| {status} {suite.mcp_server} | {suite.total_count} | "
                f"{suite.passed_count} | {suite.failed_count} | "
                f"{len(suite.all_learnings)} | {suite.duration:.1f}s |"
            )

        lines.extend(["", "## Test Details", ""])

        for suite in suites:
            lines.extend([
                f"### {suite.mcp_server}",
                ""
            ])

            for test in suite.tests:
                status = "✅" if test.passed else "❌"
                lines.append(f"**{status} {test.test_name}** ({test.duration:.2f}s)")

                if test.error:
                    lines.append(f"  - Error: {test.error}")

                # Show validation results
                passed_validations = sum(1 for v in test.validations if v.passed)
                total_validations = len(test.validations)
                lines.append(f"  - Validations: {passed_validations}/{total_validations} passed")

                # Show learnings
                if test.learnings:
                    lines.append("  - Learnings:")
                    for learning in test.learnings:
                        lines.append(f"    - {learning}")

                lines.append("")

        return "\n".join(lines)

    def generate_detailed_json(self, suites: List[TestSuiteResult]) -> Dict[str, Any]:
        """Generate detailed JSON report"""

        total_tests = sum(s.total_count for s in suites)
        total_passed = sum(s.passed_count for s in suites)
        total_failed = sum(s.failed_count for s in suites)

        return {
            'timestamp': self.timestamp,
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
            },
            'suites': [s.to_dict() for s in suites]
        }

    def generate_learnings_md(self, suites: List[TestSuiteResult]) -> str:
        """Generate learnings markdown report"""

        lines = [
            f"# MCP Test Learnings - {self.timestamp}",
            "",
            "Discoveries from comprehensive MCP testing that should inform stub enhancements.",
            ""
        ]

        for suite in suites:
            if not suite.all_learnings:
                continue

            lines.extend([
                f"## {suite.mcp_server}",
                ""
            ])

            for i, learning in enumerate(suite.all_learnings, 1):
                lines.append(f"### Learning {i}")
                lines.append(learning)
                lines.append("")

        return "\n".join(lines)

    def save_reports(self, suites: List[TestSuiteResult]):
        """Generate and save all report types"""

        # Summary markdown
        summary_md = self.generate_summary_md(suites)
        summary_path = self.output_dir / f"{self.timestamp}_summary.md"
        summary_path.write_text(summary_md)
        print(f"📊 Summary report: {summary_path}")

        # Detailed JSON
        detailed_json = self.generate_detailed_json(suites)
        json_path = self.output_dir / f"{self.timestamp}_detailed.json"
        json_path.write_text(json.dumps(detailed_json, indent=2))
        print(f"📋 Detailed report: {json_path}")

        # Learnings markdown
        learnings_md = self.generate_learnings_md(suites)
        learnings_path = self.output_dir / f"{self.timestamp}_learnings.md"
        learnings_path.write_text(learnings_md)
        print(f"💡 Learnings report: {learnings_path}")

        return {
            'summary': summary_path,
            'detailed': json_path,
            'learnings': learnings_path
        }


__all__ = ['TestResult', 'TestSuiteResult', 'TestReporter']
