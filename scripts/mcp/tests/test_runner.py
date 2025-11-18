"""MCP Test Runner

Orchestrates comprehensive testing of all MCP servers.
Runs tests, collects results, generates reports, and enhances stubs based on learnings.
"""

import sys
from pathlib import Path
import importlib.util
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.reporters import TestSuiteResult, TestReporter


class TestRunner:
    """Main test orchestrator"""

    def __init__(self, test_level: str = "smoke"):
        """
        Initialize test runner

        Args:
            test_level: Test level to run (smoke, coverage, variation, analysis, error)
        """
        self.test_level = test_level
        self.test_dir = Path(__file__).parent
        self.results_dir = self.test_dir / "test_results"
        self.results_dir.mkdir(exist_ok=True)
        self.reporter = TestReporter(self.results_dir)
        self.suite_results = []

    def discover_test_suites(self) -> list:
        """Discover all test suite files"""
        suites_dir = self.test_dir / "test_suites"
        return sorted(suites_dir.glob("test_*_mcp.py"))

    def load_test_suite(self, suite_path: Path):
        """Load a test suite module"""
        spec = importlib.util.spec_from_file_location(suite_path.stem, suite_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_suite(self, suite_path: Path) -> TestSuiteResult:
        """
        Run a single test suite

        Args:
            suite_path: Path to test suite file

        Returns:
            TestSuiteResult
        """
        print(f"\n{'=' * 80}")
        print(f"Running: {suite_path.name}")
        print(f"{'=' * 80}\n")

        # Load the test suite module
        module = self.load_test_suite(suite_path)

        # Get the test suite class
        suite_class = getattr(module, 'TestSuite', None)
        if suite_class is None:
            print(f"❌ No TestSuite class found in {suite_path.name}")
            return None

        # Run the suite
        suite = suite_class(test_level=self.test_level)
        result = suite.run()

        # Display results
        print(f"\n{'-' * 80}")
        print(f"Results: {result.passed_count}/{result.total_count} passed")
        if result.all_learnings:
            print(f"Learnings: {len(result.all_learnings)} discovered")
        print(f"Duration: {result.duration:.1f}s")
        print(f"{'-' * 80}\n")

        return result

    def enhance_stub_if_needed(self, suite_result: TestSuiteResult):
        """
        Analyze test results and enhance stub if learnings suggest improvements

        Args:
            suite_result: Test suite results with learnings
        """
        if not suite_result.all_learnings:
            print(f"ℹ️  No learnings for {suite_result.mcp_server} - stub looks good!")
            return

        print(f"\n{'=' * 80}")
        print(f"Analyzing learnings for {suite_result.mcp_server}")
        print(f"{'=' * 80}\n")

        # Display learnings
        for i, learning in enumerate(suite_result.all_learnings, 1):
            print(f"Learning {i}:")
            print(learning)
            print()

        # Determine if stub needs enhancement
        # This is where we'd analyze the learnings and decide what to update
        print("💡 Stub enhancement recommendations:")

        stub_updates = []

        for learning in suite_result.all_learnings:
            # Parse learning and determine recommended stub updates
            if "missing parameter" in learning.lower():
                stub_updates.append("Add missing parameter to function signature")
            elif "undocumented field" in learning.lower():
                stub_updates.append("Document additional response field in docstring")
            elif "quirk" in learning.lower():
                stub_updates.append("Add quirk to CRITICAL QUIRKS section")
            elif "example" in learning.lower() or "use case" in learning.lower():
                stub_updates.append("Add example demonstrating this use case")
            elif "count parameter" in learning.lower():
                stub_updates.append("Emphasize count parameter importance in docs")

        if stub_updates:
            for update in set(stub_updates):  # Deduplicate
                print(f"  - {update}")

            # Ask if user wants to apply enhancements
            print(f"\n📝 Apply these enhancements to {suite_result.mcp_server} stub?")
            print("   (This would update the Python stub file with improved documentation)")
        else:
            print("  ✅ No stub enhancements needed - documentation is complete!")

        print()

    def run_all_suites(self):
        """Run all test suites in sequence"""
        print("\n" + "=" * 80)
        print("MCP COMPREHENSIVE TEST SUITE")
        print(f"Test Level: {self.test_level}")
        print("=" * 80)

        suites = self.discover_test_suites()
        print(f"\nDiscovered {len(suites)} test suites:")
        for suite in suites:
            print(f"  - {suite.name}")
        print()

        # Run each suite
        for suite_path in suites:
            result = self.run_suite(suite_path)

            if result:
                self.suite_results.append(result)

                # IMPORTANT: Enhance stub after EACH suite (not at the end)
                self.enhance_stub_if_needed(result)

            # Rate limiting between suites
            time.sleep(2)

        # Generate final reports
        print("\n" + "=" * 80)
        print("GENERATING REPORTS")
        print("=" * 80 + "\n")

        report_paths = self.reporter.save_reports(self.suite_results)

        print("\n" + "=" * 80)
        print("TEST RUN COMPLETE")
        print("=" * 80)
        print(f"\n📊 Reports generated:")
        for report_type, path in report_paths.items():
            print(f"  {report_type}: {path}")

        # Final summary
        total_tests = sum(s.total_count for s in self.suite_results)
        total_passed = sum(s.passed_count for s in self.suite_results)
        total_failed = sum(s.failed_count for s in self.suite_results)
        total_learnings = sum(len(s.all_learnings) for s in self.suite_results)

        print(f"\n✅ Passed: {total_passed}/{total_tests}")
        print(f"❌ Failed: {total_failed}/{total_tests}")
        print(f"💡 Learnings: {total_learnings}")
        print()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP comprehensive tests")
    parser.add_argument(
        "--level",
        choices=["smoke", "coverage", "variation", "analysis", "error"],
        default="smoke",
        help="Test level to run (default: smoke)"
    )
    parser.add_argument(
        "--suite",
        help="Run specific test suite (e.g., 'fda' to run test_fda_mcp.py)"
    )

    args = parser.parse_args()

    runner = TestRunner(test_level=args.level)

    if args.suite:
        # Run specific suite
        suite_path = runner.test_dir / "test_suites" / f"test_{args.suite}_mcp.py"
        if not suite_path.exists():
            print(f"❌ Test suite not found: {suite_path}")
            sys.exit(1)

        result = runner.run_suite(suite_path)
        if result:
            runner.suite_results.append(result)
            runner.enhance_stub_if_needed(result)
            runner.reporter.save_reports(runner.suite_results)
    else:
        # Run all suites
        runner.run_all_suites()


if __name__ == "__main__":
    main()
