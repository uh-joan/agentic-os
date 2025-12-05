#!/usr/bin/env python3
"""
Source Attribution Verification Tool

Validates that skills and reports have proper source attribution according to
the source citation standards defined in CLAUDE.md and agent definitions.

Usage:
    # Verify skill return format
    python3 verify_source_attribution.py --type skill --execution-output "$(cat output.json)" --json

    # Verify report citations
    python3 verify_source_attribution.py --type report --file path/to/report.md --json

Exit codes:
    0 - Validation passed
    1 - Validation failed
    2 - Error during validation
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SourceAttributionValidator:
    """Validates source attribution in skills and reports."""

    # Required fields in source_metadata
    REQUIRED_METADATA_FIELDS = [
        'source',
        'mcp_server',
        'query_date',
        'query_params',
        'data_count',
        'data_type'
    ]

    # Valid MCP server identifiers
    VALID_MCP_SERVERS = [
        'ct_gov_mcp',
        'fda_mcp',
        'pubmed_mcp',
        'sec_mcp',
        'patents_mcp',
        'nlm_codes_mcp',
        'who_mcp',
        'datacommons_mcp',
        'healthcare_mcp',
        'financials_mcp',
        'opentargets_mcp',
        'pubchem_mcp',
        'cdc_mcp'
    ]

    # Source name mapping for validation
    SOURCE_NAME_MAPPING = {
        'ct_gov_mcp': 'ClinicalTrials.gov',
        'fda_mcp': 'FDA Drug Database',
        'pubmed_mcp': 'PubMed',
        'sec_mcp': 'SEC EDGAR',
        'patents_mcp': ['USPTO Patents', 'Google Patents'],
        'nlm_codes_mcp': 'NLM Medical Codes',
        'who_mcp': 'WHO Health Observatory',
        'datacommons_mcp': 'Data Commons',
        'healthcare_mcp': 'CMS Medicare Data',
        'financials_mcp': ['Yahoo Finance', 'FRED Economic Data'],
        'opentargets_mcp': 'Open Targets Platform',
        'pubchem_mcp': 'PubChem Database',
        'cdc_mcp': 'CDC'
    }

    def __init__(self, verbose: bool = False):
        """Initialize validator.

        Args:
            verbose: Print detailed validation steps
        """
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.recommendations = []

    def log(self, message: str):
        """Log verbose message."""
        if self.verbose:
            print(f"[DEBUG] {message}", file=sys.stderr)

    def validate_skill_output(self, execution_output: str) -> Dict:
        """Validate skill execution output has proper source metadata.

        Args:
            execution_output: String output from skill execution

        Returns:
            Validation result dictionary
        """
        self.log("Validating skill output...")
        self.errors = []
        self.warnings = []
        self.recommendations = []

        # Try to parse as JSON
        try:
            result = json.loads(execution_output)
            self.log(f"Parsed JSON result with keys: {list(result.keys())}")
        except json.JSONDecodeError as e:
            self.errors.append(f"Skill output is not valid JSON: {e}")
            return self._build_result(False)

        # Check 1: Has source_metadata key
        if 'source_metadata' not in result:
            self.errors.append("Missing 'source_metadata' key in return dict")
            self.recommendations.append("Add source_metadata dict with required fields (source, mcp_server, query_date, query_params, data_count, data_type)")
            return self._build_result(False)

        source_metadata = result['source_metadata']
        self.log(f"Found source_metadata: {source_metadata}")

        # Check 2: Has all required fields
        missing_fields = [
            field for field in self.REQUIRED_METADATA_FIELDS
            if field not in source_metadata
        ]
        if missing_fields:
            self.errors.append(f"Missing required source_metadata fields: {', '.join(missing_fields)}")

        # Check 3: Validate query_date format (ISO 8601: YYYY-MM-DD)
        if 'query_date' in source_metadata:
            date_str = source_metadata['query_date']
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                self.log(f"✓ query_date format valid: {date_str}")
            except ValueError:
                self.errors.append(f"Invalid query_date format: '{date_str}' (expected YYYY-MM-DD)")

        # Check 4: Validate mcp_server is recognized
        if 'mcp_server' in source_metadata:
            mcp_server = source_metadata['mcp_server']
            if mcp_server not in self.VALID_MCP_SERVERS:
                self.warnings.append(f"Unrecognized mcp_server: '{mcp_server}' (expected one of: {', '.join(self.VALID_MCP_SERVERS)})")

        # Check 5: Validate source name matches mcp_server
        if 'source' in source_metadata and 'mcp_server' in source_metadata:
            source = source_metadata['source']
            mcp_server = source_metadata['mcp_server']
            expected_sources = self.SOURCE_NAME_MAPPING.get(mcp_server, [])
            if isinstance(expected_sources, str):
                expected_sources = [expected_sources]

            if expected_sources and source not in expected_sources:
                self.warnings.append(f"Source name '{source}' doesn't match expected for {mcp_server}: {', '.join(expected_sources)}")

        # Check 6: data_count is integer
        if 'data_count' in source_metadata:
            if not isinstance(source_metadata['data_count'], int):
                self.errors.append(f"data_count must be integer, got {type(source_metadata['data_count']).__name__}")

        # Check 7: Has data key
        if 'data' not in result:
            self.warnings.append("Missing 'data' key (expected data to be nested under 'data' key)")

        # Check 8: Has summary with source citation
        if 'summary' in result:
            summary = result['summary']
            if 'source:' not in summary and 'Source:' not in summary:
                self.warnings.append("Summary doesn't include 'source:' citation")
                self.recommendations.append("Add source citation to summary (e.g., '...found (source: ClinicalTrials.gov, 2025-12-03)')")
        else:
            self.warnings.append("Missing 'summary' key")

        # Check 9: Validate data_count matches actual data length (if data present)
        if 'data' in result and 'data_count' in source_metadata:
            data = result['data']
            reported_count = source_metadata['data_count']

            # Try to find actual count in data
            actual_count = None
            if isinstance(data, dict):
                # Look for common count fields
                for key in ['total_count', 'count', 'length']:
                    if key in data:
                        actual_count = data[key]
                        break
                # Or count list items
                if actual_count is None:
                    for key, value in data.items():
                        if isinstance(value, list):
                            actual_count = len(value)
                            break
            elif isinstance(data, list):
                actual_count = len(data)

            if actual_count is not None and actual_count != reported_count:
                self.warnings.append(f"data_count ({reported_count}) doesn't match actual data count ({actual_count})")

        valid = len(self.errors) == 0
        return self._build_result(valid)

    def validate_report_file(self, report_path: Path) -> Dict:
        """Validate report file has proper source citations.

        Args:
            report_path: Path to markdown report file

        Returns:
            Validation result dictionary
        """
        self.log(f"Validating report: {report_path}")
        self.errors = []
        self.warnings = []
        self.recommendations = []

        if not report_path.exists():
            self.errors.append(f"Report file not found: {report_path}")
            return self._build_result(False)

        content = report_path.read_text()

        # Check 1: Has YAML frontmatter
        frontmatter = self._extract_frontmatter(content)
        if not frontmatter:
            self.errors.append("Missing YAML frontmatter")
            self.recommendations.append("Add YAML frontmatter with data_sources_mcp_verified and data_sources_internal_knowledge")
            return self._build_result(False)

        self.log(f"Found frontmatter with {len(frontmatter)} lines")

        # Check 2: Has data_sources_mcp_verified
        if 'data_sources_mcp_verified:' not in frontmatter:
            self.errors.append("Missing 'data_sources_mcp_verified' in frontmatter")
            self.recommendations.append("Add data_sources_mcp_verified section listing all MCP-sourced data")

        # Check 3: Has data_sources_internal_knowledge (even if empty)
        if 'data_sources_internal_knowledge:' not in frontmatter:
            self.warnings.append("Missing 'data_sources_internal_knowledge' in frontmatter")
            self.recommendations.append("Add data_sources_internal_knowledge section (even if empty, for transparency)")

        # Check 4: MCP data sources have proper format (source: Name, date: YYYY-MM-DD)
        mcp_sources = self._extract_mcp_sources(frontmatter)
        self.log(f"Found {len(mcp_sources)} MCP data sources")

        for i, source_line in enumerate(mcp_sources):
            # Check for (source: ..., date: YYYY-MM-DD) pattern
            if 'source:' not in source_line:
                self.warnings.append(f"MCP data source {i+1} missing 'source:' citation")
            if 'date:' not in source_line:
                self.warnings.append(f"MCP data source {i+1} missing 'date:' timestamp")

            # Validate date format
            date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', source_line)
            if date_match:
                date_str = date_match.group(1)
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    self.errors.append(f"Invalid date format in MCP source: {date_str}")

        # Check 5: Count inline citations in report body
        body = self._extract_body(content)
        citation_stats = self._count_citations(body)

        self.log(f"Citation stats: {citation_stats}")

        total_claims = citation_stats['total_sentences']
        mcp_citations = citation_stats['mcp_citations']
        literature_citations = citation_stats['literature_citations']
        internal_citations = citation_stats['internal_citations']

        if total_claims > 0:
            mcp_pct = (mcp_citations / total_claims) * 100
            internal_pct = (internal_citations / total_claims) * 100

            # Check citation percentage
            total_citations = mcp_citations + literature_citations + internal_citations
            citation_pct = (total_citations / total_claims) * 100

            if citation_pct < 70:
                self.warnings.append(f"Low citation percentage: {citation_pct:.1f}% of sentences cited (target: >70%)")
                self.recommendations.append("Add inline citations to more claims (target: >70% of major claims)")

            # Check internal knowledge usage
            if internal_pct > 20:
                self.warnings.append(f"High internal knowledge usage: {internal_pct:.1f}% (target: <20%)")
                self.recommendations.append("Reduce internal knowledge usage by querying MCP servers for more data")

        # Check 6: Tables have source attribution
        tables = self._extract_tables(body)
        tables_without_source = 0
        for table in tables:
            if not self._table_has_source(table):
                tables_without_source += 1

        if tables_without_source > 0:
            self.warnings.append(f"{tables_without_source} table(s) missing source attribution")
            self.recommendations.append("Add source attribution to tables (footer or source column)")

        valid = len(self.errors) == 0
        return self._build_result(valid, extra_stats={
            'total_claims': total_claims,
            'mcp_citations': mcp_citations,
            'literature_citations': literature_citations,
            'internal_citations': internal_citations,
            'citation_percentage': f"{citation_pct:.1f}%" if total_claims > 0 else "N/A",
            'internal_percentage': f"{internal_pct:.1f}%" if total_claims > 0 else "N/A",
            'tables_total': len(tables),
            'tables_without_source': tables_without_source
        })

    def _extract_frontmatter(self, content: str) -> str:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        return match.group(1) if match else ""

    def _extract_body(self, content: str) -> str:
        """Extract body content (after frontmatter)."""
        match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', content, re.DOTALL)
        return match.group(1) if match else content

    def _extract_mcp_sources(self, frontmatter: str) -> List[str]:
        """Extract MCP data source lines from frontmatter."""
        sources = []
        in_mcp_section = False

        for line in frontmatter.split('\n'):
            if 'data_sources_mcp_verified:' in line:
                in_mcp_section = True
                continue
            elif in_mcp_section:
                if line.strip().startswith('-'):
                    sources.append(line.strip())
                elif line.strip() and not line.startswith(' ') and ':' in line:
                    # Hit next section
                    break

        return sources

    def _count_citations(self, body: str) -> Dict[str, int]:
        """Count different types of citations in report body."""
        # Remove code blocks to avoid false positives
        body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)

        # Count sentences (rough heuristic)
        sentences = re.split(r'[.!?]\s+', body_no_code)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]  # Filter short fragments

        # Count citation types
        mcp_citations = len(re.findall(r'\(source:\s*[\w\s.]+,\s*\d{4}-\d{2}-\d{2}\)', body_no_code))
        literature_citations = len(re.findall(r'\([A-Z][a-z]+\s+et\s+al\.,\s*\w+\s+\d{4}', body_no_code))
        literature_citations += len(re.findall(r'PMID:\s*\d+', body_no_code))
        internal_citations = len(re.findall(r'\[(?:estimated|internal|analysis based on)', body_no_code))

        return {
            'total_sentences': len(sentences),
            'mcp_citations': mcp_citations,
            'literature_citations': literature_citations,
            'internal_citations': internal_citations
        }

    def _extract_tables(self, body: str) -> List[str]:
        """Extract markdown tables from body."""
        # Match markdown tables (lines with |)
        tables = []
        current_table = []

        for line in body.split('\n'):
            if '|' in line and line.strip().startswith('|'):
                current_table.append(line)
            elif current_table:
                # End of table
                tables.append('\n'.join(current_table))
                current_table = []

        if current_table:
            tables.append('\n'.join(current_table))

        return tables

    def _table_has_source(self, table: str) -> bool:
        """Check if table has source attribution."""
        # Check for **Source**: pattern after table
        # or Source column in table header
        return (
            'Source' in table or
            '**Source**:' in table or
            '**source**:' in table
        )

    def _build_result(self, valid: bool, extra_stats: Optional[Dict] = None) -> Dict:
        """Build validation result dictionary."""
        result = {
            'valid': valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': self.recommendations
        }

        if extra_stats:
            result['stats'] = extra_stats

        return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate source attribution in skills and reports'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=['skill', 'report'],
        help='Type of validation (skill or report)'
    )
    parser.add_argument(
        '--execution-output',
        help='Skill execution output (JSON string)'
    )
    parser.add_argument(
        '--file',
        help='Report file path'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    validator = SourceAttributionValidator(verbose=args.verbose)

    try:
        if args.type == 'skill':
            if not args.execution_output:
                print("Error: --execution-output required for skill validation", file=sys.stderr)
                sys.exit(2)

            result = validator.validate_skill_output(args.execution_output)

        elif args.type == 'report':
            if not args.file:
                print("Error: --file required for report validation", file=sys.stderr)
                sys.exit(2)

            result = validator.validate_report_file(Path(args.file))

        # Output results
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== Source Attribution Validation ===\n")

            if result['valid']:
                print("✅ VALIDATION PASSED")
            else:
                print("❌ VALIDATION FAILED")

            if result['errors']:
                print(f"\nErrors ({len(result['errors'])}):")
                for error in result['errors']:
                    print(f"  ❌ {error}")

            if result['warnings']:
                print(f"\nWarnings ({len(result['warnings'])}):")
                for warning in result['warnings']:
                    print(f"  ⚠️  {warning}")

            if result['recommendations']:
                print(f"\nRecommendations:")
                for rec in result['recommendations']:
                    print(f"  💡 {rec}")

            if 'stats' in result:
                print(f"\nStatistics:")
                for key, value in result['stats'].items():
                    print(f"  {key}: {value}")

        sys.exit(0 if result['valid'] else 1)

    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
