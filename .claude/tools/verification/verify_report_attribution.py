#!/usr/bin/env python3
"""
Report Source Attribution Verification Tool

Verifies that strategic analysis reports follow source attribution standards:
- MCP-verified data should be >70% of major claims
- Internal knowledge should be <20% of major claims
- All major claims must be cited with sources
- Frontmatter must include data_sources_mcp_verified and data_sources_industry_knowledge

Usage:
    python3 verify_report_attribution.py --report path/to/report.md [--json]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class ReportAttributionVerifier:
    """Verify source attribution in strategic analysis reports."""

    # Source patterns to detect
    MCP_SOURCES = [
        'ClinicalTrials.gov', 'clinicaltrials.gov',
        'FDA', 'FDA database', 'FDA Drug Database',
        'PubMed', 'SEC EDGAR', 'Open Targets',
        'WHO', 'CDC', 'Data Commons',
        'PubChem', 'CMS', 'Yahoo Finance', 'FRED'
    ]

    INTERNAL_SOURCES = ['internal', 'internal knowledge', 'industry consensus', 'estimated', 'training data']

    PUBLISHED_SOURCES = ['PMID:', 'et al.', 'NEJM', 'Lancet', 'JAMA', 'Nature', 'Science']

    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        self.content = self.report_path.read_text()
        self.frontmatter = self._parse_frontmatter()
        self.citations = self._extract_citations()

    def _parse_frontmatter(self) -> Dict:
        """Extract YAML frontmatter from report."""
        match = re.match(r'^---\n(.*?)\n---', self.content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        yaml_content = match.group(1)

        # Extract data sources sections
        mcp_section = re.search(r'data_sources_mcp_verified:(.*?)(?=\n[a-z_]+:|$)', yaml_content, re.DOTALL)
        if mcp_section:
            frontmatter['data_sources_mcp_verified'] = mcp_section.group(1).strip()

        internal_section = re.search(r'data_sources_industry_knowledge:(.*?)(?=\n[a-z_]+:|$)', yaml_content, re.DOTALL)
        if internal_section:
            frontmatter['data_sources_industry_knowledge'] = internal_section.group(1).strip()

        return frontmatter

    def _extract_citations(self) -> Dict[str, List[Dict]]:
        """Extract all inline citations from report body."""
        citations = {
            'mcp': [],
            'internal': [],
            'published': [],
            'uncited': []
        }

        # Find all (**source**: ...) patterns
        source_pattern = r'\(\*\*source\*\*:\s*([^)]+)\)'
        matches = re.finditer(source_pattern, self.content)

        for match in matches:
            citation_text = match.group(1)
            line_num = self.content[:match.start()].count('\n') + 1

            # Categorize citation
            if any(src in citation_text for src in self.MCP_SOURCES):
                citations['mcp'].append({'text': citation_text, 'line': line_num})
            elif any(src in citation_text for src in self.INTERNAL_SOURCES):
                citations['internal'].append({'text': citation_text, 'line': line_num})
            elif any(src in citation_text for src in self.PUBLISHED_SOURCES):
                citations['published'].append({'text': citation_text, 'line': line_num})
            else:
                # Unknown citation type
                citations['uncited'].append({'text': citation_text, 'line': line_num})

        return citations

    def verify(self) -> Dict:
        """Run all verification checks."""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'metrics': {}
        }

        # Check frontmatter
        if 'data_sources_mcp_verified' not in self.frontmatter:
            results['errors'].append("Missing 'data_sources_mcp_verified' section in frontmatter")
            results['valid'] = False

        if 'data_sources_industry_knowledge' not in self.frontmatter:
            results['warnings'].append("Missing 'data_sources_industry_knowledge' section in frontmatter")

        # Calculate citation metrics
        total_citations = sum(len(cites) for cites in self.citations.values())
        mcp_count = len(self.citations['mcp'])
        internal_count = len(self.citations['internal'])
        published_count = len(self.citations['published'])

        if total_citations == 0:
            results['errors'].append("No source citations found in report")
            results['valid'] = False
            return results

        mcp_percentage = (mcp_count / total_citations) * 100
        internal_percentage = (internal_count / total_citations) * 100
        published_percentage = (published_count / total_citations) * 100

        results['metrics'] = {
            'total_citations': total_citations,
            'mcp_verified': mcp_count,
            'internal_knowledge': internal_count,
            'published_literature': published_count,
            'uncategorized': len(self.citations['uncited']),
            'mcp_percentage': round(mcp_percentage, 1),
            'internal_percentage': round(internal_percentage, 1),
            'published_percentage': round(published_percentage, 1)
        }

        # Check source attribution thresholds
        # Target: >70% MCP-verified + published, <20% internal
        verified_percentage = mcp_percentage + published_percentage

        if internal_percentage > 20:
            results['errors'].append(
                f"Internal knowledge usage ({internal_percentage:.1f}%) exceeds 20% threshold. "
                f"Target: <20% internal knowledge."
            )
            results['valid'] = False
        elif internal_percentage > 15:
            results['warnings'].append(
                f"Internal knowledge usage ({internal_percentage:.1f}%) approaching 20% threshold"
            )

        if verified_percentage < 70:
            results['warnings'].append(
                f"MCP-verified + published data ({verified_percentage:.1f}%) below 70% target. "
                f"Consider citing more primary data sources."
            )

        # Check for uncited claims (sentences with numbers but no citation)
        uncited_claims = self._find_uncited_claims()
        if len(uncited_claims) > 10:
            results['warnings'].append(
                f"Found {len(uncited_claims)} potentially uncited numerical claims"
            )

        # Generate recommendations
        if internal_percentage > 20:
            results['recommendations'].append(
                f"Replace {internal_count - int(total_citations * 0.2)} internal citations with MCP-verified data"
            )
            results['recommendations'].append(
                "Run additional MCP queries to verify market sizing, efficacy data, and timelines"
            )

        if mcp_percentage < 50:
            results['recommendations'].append(
                "Increase MCP-verified citations by running more skills (FDA drugs, clinical trials, publications)"
            )

        return results

    def _find_uncited_claims(self) -> List[Tuple[int, str]]:
        """Find sentences with numerical claims but no citation."""
        uncited = []

        # Remove frontmatter
        content_match = re.search(r'^---\n.*?\n---\n(.*)', self.content, re.DOTALL)
        if content_match:
            body = content_match.group(1)
        else:
            body = self.content

        # Split into sentences
        sentences = re.split(r'[.!?]\s+', body)

        for i, sentence in enumerate(sentences):
            # Check if sentence has numbers (percentages, dollar amounts, counts)
            has_numbers = bool(re.search(r'(\d+%|\$\d+|\d+\s+(trials|patients|drugs|products))', sentence))

            # Check if sentence has citation
            has_citation = bool(re.search(r'\(\*\*source\*\*:', sentence))

            if has_numbers and not has_citation and len(sentence) > 50:
                # Potentially uncited claim
                line_num = body[:body.find(sentence)].count('\n') + 1
                uncited.append((line_num, sentence[:100] + '...'))

        return uncited[:20]  # Return first 20 examples


def main():
    parser = argparse.ArgumentParser(
        description="Verify source attribution in strategic analysis reports"
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to report markdown file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Verify report exists
    if not Path(args.report).exists():
        print(f"Error: Report file not found: {args.report}", file=sys.stderr)
        sys.exit(1)

    # Run verification
    verifier = ReportAttributionVerifier(args.report)
    results = verifier.verify()

    # Output results
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*80}")
        print(f"REPORT SOURCE ATTRIBUTION VERIFICATION")
        print(f"{'='*80}\n")

        print(f"Report: {args.report}")
        print(f"Valid: {'✅ PASS' if results['valid'] else '❌ FAIL'}\n")

        print(f"--- Citation Metrics ---")
        metrics = results['metrics']
        print(f"Total Citations: {metrics['total_citations']}")
        print(f"  MCP-Verified: {metrics['mcp_verified']} ({metrics['mcp_percentage']}%)")
        print(f"  Internal Knowledge: {metrics['internal_knowledge']} ({metrics['internal_percentage']}%)")
        print(f"  Published Literature: {metrics['published_literature']} ({metrics['published_percentage']}%)")
        if metrics['uncategorized'] > 0:
            print(f"  Uncategorized: {metrics['uncategorized']}")
        print()

        if results['errors']:
            print(f"--- Errors ({len(results['errors'])}) ---")
            for error in results['errors']:
                print(f"  ❌ {error}")
            print()

        if results['warnings']:
            print(f"--- Warnings ({len(results['warnings'])}) ---")
            for warning in results['warnings']:
                print(f"  ⚠️  {warning}")
            print()

        if results['recommendations']:
            print(f"--- Recommendations ({len(results['recommendations'])}) ---")
            for rec in results['recommendations']:
                print(f"  💡 {rec}")
            print()

        print(f"{'='*80}\n")

    sys.exit(0 if results['valid'] else 1)


if __name__ == "__main__":
    main()
