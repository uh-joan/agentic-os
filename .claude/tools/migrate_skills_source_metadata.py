#!/usr/bin/env python3
"""
Migration Helper for Adding Source Metadata to Skills

This script helps migrate existing skills to include source_metadata in their return dict.
Since each skill has unique logic, this script provides guidance and templates rather than
automatic migration.

Usage:
    python3 migrate_skills_source_metadata.py --skill-path .claude/skills/skill-name/scripts/skill.py
    python3 migrate_skills_source_metadata.py --analyze-all  # Analyze all skills
"""

import argparse
import re
from pathlib import Path
from typing import Dict, Optional


# MCP Server to Source Name Mapping
SOURCE_NAME_MAPPING = {
    'ct_gov_mcp': 'ClinicalTrials.gov',
    'fda_mcp': 'FDA Drug Database',
    'pubmed_mcp': 'PubMed',
    'sec_mcp': 'SEC EDGAR',
    'patents_mcp': 'USPTO Patents',
    'nlm_codes_mcp': 'NLM Medical Codes',
    'who_mcp': 'WHO Health Observatory',
    'datacommons_mcp': 'Data Commons',
    'healthcare_mcp': 'CMS Medicare Data',
    'financials_mcp': 'Yahoo Finance',
    'opentargets_mcp': 'Open Targets Platform',
    'pubchem_mcp': 'PubChem Database',
    'cdc_mcp': 'CDC'
}


def detect_mcp_server(code: str) -> Optional[str]:
    """Detect which MCP server is being used in the code.

    Args:
        code: Python source code

    Returns:
        MCP server identifier or None
    """
    # Look for imports from mcp.servers.*
    import_pattern = r'from mcp\.servers\.(\w+) import'
    match = re.search(import_pattern, code)

    if match:
        return match.group(1)

    return None


def detect_data_type(skill_path: Path, code: str) -> str:
    """Infer data type from skill name and code.

    Args:
        skill_path: Path to skill file
        code: Python source code

    Returns:
        Data type string
    """
    skill_name = skill_path.stem.lower()

    # Pattern matching
    if 'trial' in skill_name or 'clinical' in skill_name:
        return 'clinical_trials'
    elif 'fda' in skill_name or 'drug' in skill_name or 'approved' in skill_name:
        return 'fda_approved_drugs'
    elif 'patent' in skill_name:
        return 'patents'
    elif 'publication' in skill_name or 'pubmed' in skill_name:
        return 'publications'
    elif 'financial' in skill_name or 'sec' in skill_name:
        return 'financial_data'
    elif 'prevalence' in skill_name or 'population' in skill_name:
        return 'epidemiological_data'
    else:
        return 'unknown'


def analyze_skill(skill_path: Path) -> Dict:
    """Analyze a skill file and provide migration information.

    Args:
        skill_path: Path to skill Python file

    Returns:
        Analysis dict with migration info
    """
    if not skill_path.exists():
        return {'error': f"File not found: {skill_path}"}

    code = skill_path.read_text()

    # Detect MCP server
    mcp_server = detect_mcp_server(code)
    source_name = SOURCE_NAME_MAPPING.get(mcp_server, 'Unknown Source') if mcp_server else 'Unknown Source'

    # Detect data type
    data_type = detect_data_type(skill_path, code)

    # Check if already has source_metadata
    has_source_metadata = 'source_metadata' in code

    # Find return statements
    return_pattern = r'return\s+\{[^}]+\}'
    returns = re.findall(return_pattern, code, re.DOTALL)

    # Check if has datetime import
    has_datetime = 'from datetime import' in code or 'import datetime' in code

    return {
        'skill_path': str(skill_path),
        'skill_name': skill_path.stem,
        'mcp_server': mcp_server,
        'source_name': source_name,
        'data_type': data_type,
        'has_source_metadata': has_source_metadata,
        'has_datetime': has_datetime,
        'return_statements': len(returns),
        'needs_migration': not has_source_metadata
    }


def generate_migration_template(analysis: Dict) -> str:
    """Generate migration template code for a skill.

    Args:
        analysis: Analysis dict from analyze_skill()

    Returns:
        Template code to add to skill
    """
    mcp_server = analysis.get('mcp_server', 'unknown_mcp')
    source_name = analysis.get('source_name', 'Unknown Source')
    data_type = analysis.get('data_type', 'unknown')

    template = f"""
# Migration Template for {analysis.get('skill_name', 'skill')}
#
# Instructions:
# 1. Add datetime import at top of file (if not present):
#    from datetime import datetime
#
# 2. Wrap existing return data in 'data' key
# 3. Add 'source_metadata' dict with required fields
# 4. Update summary to include source citation

# BEFORE (example):
# return {{
#     'results': [...],
#     'total_count': 123,
#     'summary': "Found 123 results"
# }}

# AFTER:
# return {{
#     'data': {{
#         'results': [...],
#         'total_count': 123
#     }},
#     'source_metadata': {{
#         'source': '{source_name}',
#         'mcp_server': '{mcp_server}',
#         'query_date': datetime.now().strftime('%Y-%m-%d'),
#         'query_params': {{
#             # Add the parameters used in your query
#             'search_term': search_term,
#             # ... other params
#         }},
#         'data_count': 123,  # Match your actual count
#         'data_type': '{data_type}'
#     }},
#     'summary': "Found 123 results (source: {source_name}, {{datetime.now().strftime('%Y-%m-%d')}})"
# }}

# Steps:
# 1. Add datetime import if needed
# 2. Find your return statement(s)
# 3. Wrap existing data dict in 'data' key
# 4. Add 'source_metadata' dict with correct values
# 5. Update summary to cite source
# 6. Test with: python3 <skill_path>
# 7. Verify with: python3 .claude/tools/verification/verify_source_attribution.py --type skill --execution-output "$(python3 <skill_path>)"
"""

    return template


def analyze_all_skills(skills_dir: Path) -> list:
    """Analyze all skills in the skills directory.

    Args:
        skills_dir: Path to skills directory

    Returns:
        List of analysis dicts
    """
    results = []

    # Find all skill Python files (both folder and flat structure)
    skill_files = list(skills_dir.glob('*/scripts/*.py'))  # Folder structure
    skill_files.extend(skills_dir.glob('*.py'))  # Flat structure

    for skill_file in skill_files:
        # Skip __init__.py and test files
        if skill_file.name == '__init__.py' or 'test' in skill_file.name.lower():
            continue

        analysis = analyze_skill(skill_file)
        results.append(analysis)

    return results


def print_analysis_report(analyses: list):
    """Print analysis report for all skills.

    Args:
        analyses: List of analysis dicts
    """
    print("\n" + "="*70)
    print(" Skills Migration Analysis Report")
    print("="*70 + "\n")

    total = len(analyses)
    needs_migration = sum(1 for a in analyses if a.get('needs_migration', False))
    already_migrated = total - needs_migration

    print(f"Total skills analyzed: {total}")
    print(f"Already has source_metadata: {already_migrated} ({already_migrated/total*100:.1f}%)")
    print(f"Needs migration: {needs_migration} ({needs_migration/total*100:.1f}%)")
    print()

    # Group by MCP server
    by_server = {}
    for analysis in analyses:
        if analysis.get('needs_migration'):
            server = analysis.get('mcp_server', 'unknown')
            if server not in by_server:
                by_server[server] = []
            by_server[server].append(analysis)

    print("Skills needing migration by MCP server:")
    # Sort with None values last
    sorted_servers = sorted(by_server.items(), key=lambda x: (x[0] is None, x[0] or ''))
    for server, skills in sorted_servers:
        server_name = server if server else 'unknown'
        print(f"  {server_name}: {len(skills)} skills")

    print("\n" + "="*70)
    print("Skills needing migration (first 20):")
    print("="*70 + "\n")

    for i, analysis in enumerate(analyses[:20]):
        if analysis.get('needs_migration'):
            print(f"{i+1}. {analysis.get('skill_name')}")
            print(f"   Path: {analysis.get('skill_path')}")
            print(f"   MCP Server: {analysis.get('mcp_server')}")
            print(f"   Source: {analysis.get('source_name')}")
            print(f"   Data Type: {analysis.get('data_type')}")
            print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Migration helper for adding source metadata to skills'
    )
    parser.add_argument(
        '--skill-path',
        help='Path to specific skill file to analyze'
    )
    parser.add_argument(
        '--analyze-all',
        action='store_true',
        help='Analyze all skills in .claude/skills/'
    )
    parser.add_argument(
        '--generate-template',
        action='store_true',
        help='Generate migration template code'
    )

    args = parser.parse_args()

    if args.analyze_all:
        # Analyze all skills
        skills_dir = Path('.claude/skills')
        if not skills_dir.exists():
            print(f"Error: Skills directory not found: {skills_dir}")
            return 1

        analyses = analyze_all_skills(skills_dir)
        print_analysis_report(analyses)

    elif args.skill_path:
        # Analyze specific skill
        skill_path = Path(args.skill_path)
        analysis = analyze_skill(skill_path)

        print("\n" + "="*70)
        print(f" Analysis: {analysis.get('skill_name')}")
        print("="*70 + "\n")

        for key, value in analysis.items():
            print(f"{key}: {value}")

        if args.generate_template:
            print("\n" + "="*70)
            print(" Migration Template")
            print("="*70)
            print(generate_migration_template(analysis))

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
