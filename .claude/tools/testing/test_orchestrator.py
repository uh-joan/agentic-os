#!/usr/bin/env python3
"""
Test Orchestrator - Closes the agentic loop for skill testing

Workflow:
1. Test skill
2. If tests fail, analyze failure
3. Generate repair instructions for pharma-search-specialist
4. (Agent invokes pharma-search-specialist with instructions)
5. Test repaired skill
6. Repeat until success or max iterations

This script provides the analysis and instructions - the actual agent
invocation happens in Claude Code's main conversation.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from test_runner import SkillTestRunner, TestStatus, SkillTestReport


@dataclass
class RepairInstruction:
    """Instructions for repairing a failing skill"""
    issue_type: str
    severity: str  # critical | high | medium | low
    description: str
    suggested_fix: str
    code_location: Optional[str] = None


@dataclass
class OrchestrationResult:
    """Result of test orchestration"""
    skill_name: str
    skill_path: str
    iteration: int
    max_iterations: int
    test_report: SkillTestReport
    needs_repair: bool
    repair_instructions: List[RepairInstruction]
    agent_prompt: Optional[str] = None  # Prompt for pharma-search-specialist


class TestOrchestrator:
    """
    Orchestrates skill testing with self-healing via agent invocation
    """

    def __init__(self, project_root: Path = None, max_iterations: int = 3):
        self.project_root = project_root or Path.cwd()
        self.test_runner = SkillTestRunner(project_root)
        self.max_iterations = max_iterations

    def orchestrate_test(
        self,
        skill_path: str,
        args: List[str] = None,
        iteration: int = 1
    ) -> OrchestrationResult:
        """
        Run test and generate repair instructions if needed

        Args:
            skill_path: Path to skill script
            args: Optional arguments for skill
            iteration: Current iteration (1-based)

        Returns:
            OrchestrationResult with test report and repair instructions
        """
        # Run tests
        test_report = self.test_runner.test_skill(skill_path, args)

        # Check if repair is needed
        needs_repair = test_report.overall_status != TestStatus.PASSED.value

        repair_instructions = []
        agent_prompt = None

        if needs_repair and iteration < self.max_iterations:
            # Analyze failures and generate repair instructions
            repair_instructions = self._analyze_failures(test_report)

            # Generate agent prompt
            agent_prompt = self._generate_agent_prompt(
                skill_path,
                test_report,
                repair_instructions,
                iteration
            )

        return OrchestrationResult(
            skill_name=test_report.skill_name,
            skill_path=test_report.skill_path,
            iteration=iteration,
            max_iterations=self.max_iterations,
            test_report=test_report,
            needs_repair=needs_repair,
            repair_instructions=repair_instructions,
            agent_prompt=agent_prompt
        )

    def _analyze_failures(self, report: SkillTestReport) -> List[RepairInstruction]:
        """Analyze test failures and generate repair instructions"""
        instructions = []

        for test in report.tests:
            if test.status == TestStatus.FAILED.value or test.status == TestStatus.ERROR.value:
                instruction = self._create_repair_instruction(test, report)
                if instruction:
                    instructions.append(instruction)

        return instructions

    def _create_repair_instruction(
        self,
        test_result,
        report: SkillTestReport
    ) -> Optional[RepairInstruction]:
        """Create repair instruction for a failed test"""

        test_type = test_result.test_type

        if test_type == "syntax":
            return RepairInstruction(
                issue_type="syntax_error",
                severity="critical",
                description=f"Python syntax error: {test_result.message}",
                suggested_fix="Fix syntax error in the Python code. Ensure proper indentation, closing brackets, and valid Python syntax.",
                code_location=test_result.details.get('line') if test_result.details else None
            )

        elif test_type == "import":
            return RepairInstruction(
                issue_type="import_error",
                severity="critical",
                description=f"Import failed: {test_result.message}",
                suggested_fix=self._analyze_import_error(test_result, report)
            )

        elif test_type == "execution":
            return RepairInstruction(
                issue_type="execution_error",
                severity="high",
                description=f"Execution failed: {test_result.message}",
                suggested_fix=self._analyze_execution_error(test_result, report)
            )

        elif test_type == "data":
            return RepairInstruction(
                issue_type="data_validation_error",
                severity="high",
                description=f"Data validation failed: {test_result.message}",
                suggested_fix=self._analyze_data_error(test_result, report)
            )

        elif test_type == "schema":
            return RepairInstruction(
                issue_type="schema_validation_error",
                severity="medium",
                description=f"Schema validation failed: {test_result.message}",
                suggested_fix=self._analyze_schema_error(test_result, report)
            )

        return None

    def _analyze_import_error(self, test_result, report: SkillTestReport) -> str:
        """Analyze import error and suggest fix"""
        error = test_result.details.get('error', '') if test_result.details else ''

        if 'mcp.servers' in error or 'mcp.client' in error:
            return """Fix MCP import path. Ensure:
1. Import uses correct path: `from mcp.servers.{server}_mcp import {function}`
2. sys.path includes .claude directory: `sys.path.insert(0, ".claude")`
3. MCP server exists in .claude/mcp/servers/"""

        elif 'No module named' in error:
            module = error.split("'")[1] if "'" in error else "unknown"
            return f"""Install missing dependency: {module}
Either:
1. Add to requirements.txt
2. Use stdlib alternative
3. Import conditionally with try/except"""

        else:
            return """Fix import error. Review:
1. All import statements are correct
2. Required modules are installed
3. sys.path is configured correctly"""

    def _analyze_execution_error(self, test_result, report: SkillTestReport) -> str:
        """Analyze execution error and suggest fix"""
        stderr = test_result.details.get('stderr', '') if test_result.details else ''
        stdout = test_result.details.get('stdout', '') if test_result.details else ''

        # Common error patterns
        if 'KeyError' in stderr:
            return """Fix KeyError in data parsing:
1. Use .get() method instead of direct dictionary access
2. Add error handling for missing keys
3. Validate response structure before accessing fields"""

        elif 'IndexError' in stderr:
            return """Fix IndexError:
1. Check list length before accessing indices
2. Add bounds checking
3. Handle empty response cases"""

        elif 'AttributeError' in stderr:
            return """Fix AttributeError:
1. Validate object type before accessing attributes
2. Check if attribute exists with hasattr()
3. Handle None values properly"""

        elif 'TypeError' in stderr:
            return """Fix TypeError:
1. Validate data types before operations
2. Convert types explicitly (str(), int(), etc.)
3. Handle None/null values"""

        elif 'Connection' in stderr or 'timeout' in stderr.lower():
            return """Fix connection/timeout issue:
1. Add retry logic with exponential backoff
2. Increase timeout values
3. Add error handling for network failures"""

        elif 'API' in stderr or 'rate limit' in stderr.lower():
            return """Fix API error:
1. Verify API parameters are correct
2. Add rate limiting/throttling
3. Handle API error responses gracefully"""

        elif report.error_output and 'No results' in report.error_output:
            return """Query returned no results. This may indicate:
1. Query parameters are too restrictive
2. Search terms need adjustment
3. Date range needs expansion
4. Server has no matching data

Review query logic and parameters."""

        else:
            return f"""Fix execution error:
Review error output and fix the issue:
{stderr[:500]}

Common fixes:
1. Add error handling (try/except)
2. Validate inputs before processing
3. Handle edge cases (empty data, None values)
4. Add defensive programming checks"""

    def _analyze_data_error(self, test_result, report: SkillTestReport) -> str:
        """Analyze data validation error and suggest fix"""
        message = test_result.message

        if "No data returned" in message:
            return """Skill returned no output. Ensure:
1. print() statements output results
2. Function returns data
3. __main__ block calls function and prints results"""

        elif "zero results" in message.lower():
            pattern = test_result.details.get('pattern_matched', '') if test_result.details else ''
            return f"""Query returned zero results (matched pattern: "{pattern}").

This may indicate:
1. Query parameters are too restrictive - try broader search terms
2. Date range is too narrow - expand time window
3. Filters exclude all results - review filter logic
4. Server has no matching data - verify query is valid

Review and adjust query logic to return results."""

        else:
            return """Fix data validation issue:
1. Ensure skill returns meaningful data
2. Verify query logic is correct
3. Add logging to debug data flow"""

    def _analyze_schema_error(self, test_result, report: SkillTestReport) -> str:
        """Analyze schema validation error and suggest fix"""
        expected = test_result.details.get('expected_patterns', []) if test_result.details else []
        matched = test_result.details.get('matched_patterns', []) if test_result.details else []

        return f"""Output schema doesn't match expected format.

Expected patterns: {', '.join(expected)}
Matched patterns: {', '.join(matched)}

Ensure output includes:
1. Standard field names for this skill type
2. Properly formatted results
3. Summary statistics (count, totals, etc.)

Review output format and align with skill type conventions."""

    def _generate_agent_prompt(
        self,
        skill_path: str,
        report: SkillTestReport,
        instructions: List[RepairInstruction],
        iteration: int
    ) -> str:
        """Generate prompt for pharma-search-specialist to repair skill"""

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_instructions = sorted(
            instructions,
            key=lambda x: severity_order.get(x.severity, 999)
        )

        prompt = f"""SKILL REPAIR REQUEST (Iteration {iteration}/{self.max_iterations})

Skill: {report.skill_name}
Path: {skill_path}
Test Status: {report.overall_status}
Tests: {report.passed_tests}/{report.total_tests} passed

ISSUES DETECTED:
"""

        for i, instr in enumerate(sorted_instructions, 1):
            prompt += f"""
{i}. [{instr.severity.upper()}] {instr.issue_type}
   Description: {instr.description}
   Suggested Fix: {instr.suggested_fix}
"""
            if instr.code_location:
                prompt += f"   Location: Line {instr.code_location}\n"

        if report.execution_output:
            prompt += f"""
EXECUTION OUTPUT:
{report.execution_output[:1000]}
"""

        if report.error_output:
            prompt += f"""
ERROR OUTPUT:
{report.error_output[:1000]}
"""

        prompt += f"""

TASK:
Read the skill file at {skill_path} and fix ALL issues listed above.

REQUIREMENTS:
1. Fix critical issues first (syntax, imports)
2. Fix high-severity issues (execution, data)
3. Fix medium-severity issues (schema)
4. Ensure skill is executable standalone (has if __name__ == "__main__":)
5. Add error handling and defensive programming
6. Test locally before returning code

Return the complete fixed skill code ready to save to {skill_path}.
"""

        return prompt

    def generate_summary(self, result: OrchestrationResult) -> str:
        """Generate human-readable summary"""
        summary = f"""
{'='*60}
Test Orchestration Summary
{'='*60}
Skill: {result.skill_name}
Path: {result.skill_path}
Iteration: {result.iteration}/{result.max_iterations}
Status: {result.test_report.overall_status.upper()}
Tests: {result.test_report.passed_tests}/{result.test_report.total_tests} passed
{'='*60}
"""

        if result.needs_repair:
            summary += f"\nREPAIR NEEDED: {len(result.repair_instructions)} issue(s) detected\n\n"

            for i, instr in enumerate(result.repair_instructions, 1):
                summary += f"{i}. [{instr.severity.upper()}] {instr.issue_type}\n"
                summary += f"   {instr.description}\n\n"

            if result.agent_prompt:
                summary += f"\nNEXT STEP: Invoke pharma-search-specialist with repair prompt\n"
        else:
            summary += f"\n✓ ALL TESTS PASSED - Skill is healthy!\n"

        return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Orchestrate skill testing with repair')
    parser.add_argument('skill_path', help='Path to skill script')
    parser.add_argument('--args', nargs='*', help='Arguments to pass to skill')
    parser.add_argument('--iteration', type=int, default=1, help='Current iteration (1-based)')
    parser.add_argument('--max-iterations', type=int, default=3, help='Max repair iterations')
    parser.add_argument('--json', action='store_true', help='Output JSON format')

    args = parser.parse_args()

    orchestrator = TestOrchestrator(
        max_iterations=args.max_iterations
    )

    result = orchestrator.orchestrate_test(
        skill_path=args.skill_path,
        args=args.args,
        iteration=args.iteration
    )

    if args.json:
        # Convert to dict for JSON serialization
        result_dict = {
            'skill_name': result.skill_name,
            'skill_path': result.skill_path,
            'iteration': result.iteration,
            'max_iterations': result.max_iterations,
            'needs_repair': result.needs_repair,
            'test_report': asdict(result.test_report),
            'repair_instructions': [asdict(i) for i in result.repair_instructions],
            'agent_prompt': result.agent_prompt
        }
        print(json.dumps(result_dict, indent=2))
    else:
        # Human-readable output
        print(orchestrator.generate_summary(result))

        # Print agent prompt if repair needed
        if result.agent_prompt and result.iteration < result.max_iterations:
            print(f"{'='*60}")
            print("AGENT REPAIR PROMPT")
            print(f"{'='*60}")
            print(result.agent_prompt)

    # Exit code: 0 if passed, 1 if needs repair, 2 if max iterations exceeded
    if not result.needs_repair:
        sys.exit(0)
    elif result.iteration < result.max_iterations:
        sys.exit(1)  # Needs repair, more iterations available
    else:
        sys.exit(2)  # Max iterations exceeded


if __name__ == "__main__":
    main()
