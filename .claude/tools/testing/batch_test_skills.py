#!/usr/bin/env python3
"""
Batch Skill Tester - Test all skills and update health status

Tests all skills in the library and:
- Generates health report
- Updates health status in index
- Identifies skills needing repair
- Provides summary statistics
"""

import sys
import json
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from test_runner import SkillTestRunner, TestStatus
sys.path.insert(0, str(Path(__file__).parent.parent / "skill_discovery"))
from health_check import HealthStatus
from index_updater import update_skill_health


@dataclass
class BatchTestSummary:
    """Summary of batch testing results"""
    total_skills: int
    healthy_skills: int
    broken_skills: int
    untested_skills: int
    test_results: List[Dict]


class BatchSkillTester:
    """Test all skills in the library"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.skills_dir = self.project_root / ".claude" / "skills"
        self.index_path = self.skills_dir / "index.json"
        self.test_runner = SkillTestRunner(project_root)

    def test_all_skills(self, update_health: bool = False) -> BatchTestSummary:
        """
        Test all skills in index

        Args:
            update_health: Update health status in index

        Returns:
            BatchTestSummary with results
        """
        # Load index
        with open(self.index_path, 'r') as f:
            index = json.load(f)

        skills = index.get('skills', [])
        test_results = []
        healthy = 0
        broken = 0
        untested = 0

        print(f"Testing {len(skills)} skills...\n")

        for i, skill in enumerate(skills, 1):
            skill_name = skill['name']
            folder = skill.get('folder', skill_name)
            script_name = f"{skill_name}.py"
            script_path = f".claude/skills/{folder}/scripts/{script_name}"

            # Check if skill file exists
            full_path = self.project_root / script_path
            if not full_path.exists():
                print(f"{i}/{len(skills)} [SKIP] {skill_name}: File not found")
                untested += 1
                test_results.append({
                    'skill_name': skill_name,
                    'status': 'untested',
                    'reason': 'File not found',
                    'path': script_path
                })
                continue

            # Test skill
            print(f"{i}/{len(skills)} [TEST] {skill_name}...", end=' ')

            try:
                report = self.test_runner.test_skill(script_path)

                if report.overall_status == TestStatus.PASSED.value:
                    print(f"✓ PASSED ({report.passed_tests}/{report.total_tests})")
                    healthy += 1

                    if update_health:
                        update_skill_health(skill_name, HealthStatus.HEALTHY, [])

                    test_results.append({
                        'skill_name': skill_name,
                        'status': 'passed',
                        'tests_passed': report.passed_tests,
                        'tests_total': report.total_tests,
                        'path': script_path
                    })
                else:
                    print(f"✗ FAILED ({report.passed_tests}/{report.total_tests})")
                    broken += 1

                    # Extract failure reasons
                    issues = [
                        f"{t.test_type}: {t.message}"
                        for t in report.tests
                        if t.status in [TestStatus.FAILED.value, TestStatus.ERROR.value]
                    ]

                    if update_health:
                        update_skill_health(skill_name, HealthStatus.BROKEN, issues)

                    test_results.append({
                        'skill_name': skill_name,
                        'status': 'failed',
                        'tests_passed': report.passed_tests,
                        'tests_total': report.total_tests,
                        'issues': issues,
                        'path': script_path
                    })

            except Exception as e:
                print(f"⚠ ERROR: {str(e)}")
                broken += 1

                if update_health:
                    update_skill_health(skill_name, HealthStatus.BROKEN, [str(e)])

                test_results.append({
                    'skill_name': skill_name,
                    'status': 'error',
                    'error': str(e),
                    'path': script_path
                })

        return BatchTestSummary(
            total_skills=len(skills),
            healthy_skills=healthy,
            broken_skills=broken,
            untested_skills=untested,
            test_results=test_results
        )

    def generate_report(self, summary: BatchTestSummary, output_format: str = 'text') -> str:
        """Generate test report"""
        if output_format == 'json':
            return json.dumps({
                'total_skills': summary.total_skills,
                'healthy_skills': summary.healthy_skills,
                'broken_skills': summary.broken_skills,
                'untested_skills': summary.untested_skills,
                'health_percentage': round(summary.healthy_skills / summary.total_skills * 100, 1) if summary.total_skills > 0 else 0,
                'test_results': summary.test_results
            }, indent=2)
        else:
            report = f"""
{'='*60}
Skill Library Health Report
{'='*60}
Total Skills:    {summary.total_skills}
✓ Healthy:       {summary.healthy_skills} ({summary.healthy_skills/summary.total_skills*100:.1f}%)
✗ Broken:        {summary.broken_skills} ({summary.broken_skills/summary.total_skills*100:.1f}%)
○ Untested:      {summary.untested_skills}
{'='*60}

"""

            # Failed skills
            if summary.broken_skills > 0:
                report += "FAILED SKILLS:\n\n"
                for result in summary.test_results:
                    if result['status'] in ['failed', 'error']:
                        report += f"✗ {result['skill_name']}\n"
                        report += f"  Path: {result['path']}\n"

                        if 'issues' in result:
                            report += f"  Issues:\n"
                            for issue in result['issues']:
                                report += f"    - {issue}\n"

                        if 'error' in result:
                            report += f"  Error: {result['error']}\n"

                        report += "\n"

            # Untested skills
            if summary.untested_skills > 0:
                report += f"{'='*60}\n"
                report += "UNTESTED SKILLS:\n\n"
                for result in summary.test_results:
                    if result['status'] == 'untested':
                        report += f"○ {result['skill_name']}\n"
                        report += f"  Reason: {result['reason']}\n"
                        report += f"  Path: {result['path']}\n\n"

            return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Batch test all skills')
    parser.add_argument('--update-health', action='store_true', help='Update health status in index')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--output', type=str, help='Save report to file')

    args = parser.parse_args()

    tester = BatchSkillTester()
    summary = tester.test_all_skills(update_health=args.update_health)

    # Generate report
    output_format = 'json' if args.json else 'text'
    report = tester.generate_report(summary, output_format)

    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {args.output}")
    else:
        print(report)

    # Exit code based on health
    if summary.broken_skills == 0:
        sys.exit(0)  # All healthy
    elif summary.healthy_skills > summary.broken_skills:
        sys.exit(1)  # Mostly healthy, some broken
    else:
        sys.exit(2)  # Mostly broken


if __name__ == "__main__":
    main()
