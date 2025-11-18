#!/usr/bin/env python3
"""
Comprehensive Obesity Clinical Trials Pipeline Analysis
"""
import sys
import re
from pathlib import Path

# Add scripts directory to path (handles execution from any location)
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent.parent.parent
sys.path.insert(0, str(root_dir / 'scripts'))

from mcp.client import get_client

def extract_count(text):
    """Extract total count from MCP response"""
    match = re.search(r'(\d+) of ([\d,]+) studies found', text)
    return int(match.group(2).replace(',', '')) if match else 0

def main():
    client = get_client('ct-gov-mcp')

    print('=' * 100)
    print('COMPREHENSIVE OBESITY CLINICAL TRIALS PIPELINE ANALYSIS - UNITED STATES')
    print('=' * 100)

    # Phase 1: Overview
    print('\n[1/7] Gathering comprehensive trial overview...')
    overview = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'location': 'United States',
        'pageSize': 10
    })
    total_trials = extract_count(overview)

    # Phase 2: By Phase Analysis
    print('[2/7] Analyzing trials by phase...')
    phases = {}
    for phase in ['EARLY_PHASE1', 'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4']:
        result = client.call_tool('ct_gov_studies', {
            'method': 'search',
            'condition': 'obesity',
            'phase': phase,
            'location': 'United States',
            'pageSize': 10
        })
        phases[phase] = extract_count(result)

    # Phase 3: Skip intervention type (parameter not supported)
    print('[3/7] Skipping intervention type analysis (API limitation)...')
    interventions = {}

    # Phase 4: By Status
    print('[4/7] Analyzing trial status distribution...')
    statuses = {}
    for status in ['recruiting', 'active_not_recruiting', 'completed', 'not_yet_recruiting']:
        result = client.call_tool('ct_gov_studies', {
            'method': 'search',
            'condition': 'obesity',
            'status': status,
            'location': 'United States',
            'pageSize': 10
        })
        statuses[status] = extract_count(result)

    # Phase 5: Industry vs Academic
    print('[5/7] Analyzing sponsor types...')
    industry_result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'funderType': 'industry',
        'location': 'United States',
        'pageSize': 10
    })
    industry_count = extract_count(industry_result)

    academic_result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'funderType': 'other',
        'location': 'United States',
        'pageSize': 10
    })
    academic_count = extract_count(academic_result)

    # Phase 6: Skip recent activity (date parameter issues)
    print('[6/7] Skipping recent activity analysis (API limitation)...')
    recent_count = 0

    # Phase 7: Key Drug Classes
    print('[7/7] Analyzing key drug intervention classes...')
    drugs = {}
    for name, term in [('GLP-1', 'GLP-1'), ('Semaglutide', 'semaglutide'),
                        ('Liraglutide', 'liraglutide'), ('Tirzepatide', 'tirzepatide'),
                        ('Metformin', 'metformin')]:
        result = client.call_tool('ct_gov_studies', {
            'method': 'search',
            'condition': 'obesity',
            'intervention': term,
            'location': 'United States',
            'pageSize': 10
        })
        drugs[name] = extract_count(result)

    # Generate Summary
    print('\n' + '=' * 100)
    print('ANALYSIS RESULTS')
    print('=' * 100)

    print(f'\n1. OVERALL LANDSCAPE')
    print(f'   Total obesity trials in US: {total_trials:,}')

    print(f'\n2. PHASE DISTRIBUTION')
    for phase, count in phases.items():
        phase_name = phase.replace('_', ' ').title()
        percentage = (count / total_trials * 100) if total_trials > 0 else 0
        print(f'   {phase_name:20s}: {count:4d} trials ({percentage:5.1f}%)')

    # Skipping intervention type section
    # print(f'\n3. INTERVENTION TYPE DISTRIBUTION')

    print(f'\n4. TRIAL STATUS (COMPETITIVE ACTIVITY)')
    for status, count in statuses.items():
        status_name = status.replace('_', ' ').title()
        percentage = (count / total_trials * 100) if total_trials > 0 else 0
        print(f'   {status_name:25s}: {count:4d} trials ({percentage:5.1f}%)')

    print(f'\n5. SPONSOR TYPE DISTRIBUTION')
    print(f'   Industry-sponsored:     {industry_count:4d} trials ({industry_count/total_trials*100:5.1f}%)')
    print(f'   Academic/Other:         {academic_count:4d} trials ({academic_count/total_trials*100:5.1f}%)')

    # Skipping recent activity section
    # print(f'\n6. RECENT ACTIVITY (2023-2025)')

    print(f'\n7. KEY DRUG CLASSES (COMPETITIVE LANDSCAPE)')
    sorted_drugs = sorted(drugs.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_drugs:
        print(f'   {name:20s}: {count:4d} trials')

    # Strategic Insights
    print(f'\n' + '=' * 100)
    print('STRATEGIC INSIGHTS')
    print('=' * 100)

    recruiting_count = statuses.get('recruiting', 0)
    phase3_count = phases.get('PHASE3', 0)
    glp1_count = drugs.get('GLP-1', 0)
    sema_count = drugs.get('Semaglutide', 0)

    print(f'\n• Market Maturity: {"HIGH" if phase3_count > 50 else "MODERATE" if phase3_count > 20 else "EMERGING"}')
    print(f'  - {phase3_count} Phase 3 trials indicate mature competitive landscape')

    print(f'\n• Current Competition: {"INTENSE" if recruiting_count > 100 else "MODERATE"}')
    print(f'  - {recruiting_count} actively recruiting trials competing for patients')

    print(f'\n• Industry Activity: {"High" if total_trials > 0 and industry_count/total_trials > 0.4 else "Moderate"}')
    print(f'  - Industry funding: {(industry_count/total_trials*100 if total_trials > 0 else 0):.1f}%')

    print(f'\n• GLP-1 Dominance: {"VERY HIGH" if glp1_count > 50 else "HIGH" if glp1_count > 30 else "MODERATE"}')
    print(f'  - {glp1_count} GLP-1 trials ({(glp1_count/total_trials*100 if total_trials > 0 else 0):.1f}% of all obesity trials)')
    print(f'  - Semaglutide: {sema_count} trials (market leader)')

    # Skipping pipeline velocity
    # print(f'\n• Pipeline Velocity')

    print('\n' + '=' * 100)
    print('ANALYSIS COMPLETE')
    print('=' * 100)

if __name__ == '__main__':
    main()
