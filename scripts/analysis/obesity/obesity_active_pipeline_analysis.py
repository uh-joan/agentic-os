#!/usr/bin/env python3
"""
Comprehensive Obesity Clinical Trials Pipeline Analysis - ACTIVE TRIALS ONLY
(Recruiting + Active Not Recruiting)
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
    print('OBESITY CLINICAL TRIALS PIPELINE ANALYSIS - ACTIVE TRIALS ONLY (RECRUITING + ACTIVE)')
    print('=' * 100)

    # Phase 1: Recruiting trials overview
    print('\n[1/6] Gathering recruiting trials...')
    recruiting = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'status': 'recruiting',
        'location': 'United States',
        'pageSize': 10
    })
    recruiting_count = extract_count(recruiting)

    # Phase 1b: Active not recruiting trials
    print('[1b/6] Gathering active not recruiting trials...')
    active_not_recruiting = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'status': 'active_not_recruiting',
        'location': 'United States',
        'pageSize': 10
    })
    active_count = extract_count(active_not_recruiting)

    total_active = recruiting_count + active_count

    # Phase 2: Active trials by phase
    print('[2/6] Analyzing active trials by phase...')
    phases = {}
    for phase in ['EARLY_PHASE1', 'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4']:
        result = client.call_tool('ct_gov_studies', {
            'method': 'search',
            'condition': 'obesity',
            'phase': phase,
            'status': 'recruiting OR active_not_recruiting',
            'location': 'United States',
            'pageSize': 10
        })
        phases[phase] = extract_count(result)

    # Phase 3: Active trials by sponsor type
    print('[3/6] Analyzing active trials by sponsor type...')
    industry_result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'funderType': 'industry',
        'status': 'recruiting OR active_not_recruiting',
        'location': 'United States',
        'pageSize': 10
    })
    industry_count = extract_count(industry_result)

    academic_result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'funderType': 'other',
        'status': 'recruiting OR active_not_recruiting',
        'location': 'United States',
        'pageSize': 10
    })
    academic_count = extract_count(academic_result)

    # Phase 4: Key Drug Classes (active trials only)
    print('[4/6] Analyzing active trials by key drug classes...')
    drugs = {}
    for name, term in [('GLP-1', 'GLP-1'), ('Semaglutide', 'semaglutide'),
                        ('Liraglutide', 'liraglutide'), ('Tirzepatide', 'tirzepatide'),
                        ('Metformin', 'metformin'), ('Orlistat', 'orlistat'),
                        ('Phentermine', 'phentermine')]:
        result = client.call_tool('ct_gov_studies', {
            'method': 'search',
            'condition': 'obesity',
            'intervention': term,
            'status': 'recruiting OR active_not_recruiting',
            'location': 'United States',
            'pageSize': 10
        })
        drugs[name] = extract_count(result)

    # Phase 5: Not yet recruiting (pipeline preview)
    print('[5/6] Analyzing pipeline (not yet recruiting)...')
    pipeline_result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'status': 'not_yet_recruiting',
        'location': 'United States',
        'pageSize': 10
    })
    pipeline_count = extract_count(pipeline_result)

    # Phase 6: Recently completed (last reference point)
    print('[6/6] Reference: recently completed trials...')
    completed_result = client.call_tool('ct_gov_studies', {
        'method': 'search',
        'condition': 'obesity',
        'status': 'completed',
        'location': 'United States',
        'pageSize': 10
    })
    completed_count = extract_count(completed_result)

    # Generate Summary
    print('\n' + '=' * 100)
    print('ANALYSIS RESULTS - ACTIVE TRIALS ONLY')
    print('=' * 100)

    print(f'\n1. ACTIVE TRIAL LANDSCAPE')
    print(f'   Recruiting:                  {recruiting_count:4d} trials')
    print(f'   Active (not recruiting):     {active_count:4d} trials')
    print(f'   ─────────────────────────────────────────')
    print(f'   TOTAL ACTIVE:                {total_active:4d} trials')
    print(f'   Pipeline (not yet recruiting): {pipeline_count:3d} trials')
    print(f'   Completed (reference):       {completed_count:4d} trials')

    print(f'\n2. ACTIVE TRIALS BY PHASE')
    phase_total = sum(phases.values())
    for phase, count in phases.items():
        phase_name = phase.replace('_', ' ').title()
        percentage = (count / phase_total * 100) if phase_total > 0 else 0
        active_pct = (count / total_active * 100) if total_active > 0 else 0
        print(f'   {phase_name:20s}: {count:4d} trials ({percentage:5.1f}% of phased, {active_pct:5.1f}% of all active)')

    print(f'\n3. ACTIVE TRIALS BY SPONSOR TYPE')
    print(f'   Industry-sponsored:          {industry_count:4d} trials ({industry_count/total_active*100:5.1f}%)')
    print(f'   Academic/Other:              {academic_count:4d} trials ({academic_count/total_active*100:5.1f}%)')

    print(f'\n4. ACTIVE TRIALS BY KEY DRUG CLASS (COMPETITIVE LANDSCAPE)')
    sorted_drugs = sorted(drugs.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_drugs:
        if count > 0:
            pct = (count / total_active * 100) if total_active > 0 else 0
            print(f'   {name:20s}: {count:4d} active trials ({pct:4.1f}% of active trials)')

    # Strategic Insights
    print(f'\n' + '=' * 100)
    print('STRATEGIC INSIGHTS - ACTIVE COMPETITIVE LANDSCAPE')
    print('=' * 100)

    phase3_count = phases.get('PHASE3', 0)
    phase2_count = phases.get('PHASE2', 0)
    glp1_count = drugs.get('GLP-1', 0)
    sema_count = drugs.get('Semaglutide', 0)
    tirz_count = drugs.get('Tirzepatide', 0)

    print(f'\n• Current Active Competition: {"VERY INTENSE" if recruiting_count > 500 else "INTENSE" if recruiting_count > 300 else "MODERATE"}')
    print(f'  - {recruiting_count} trials actively recruiting patients RIGHT NOW')
    print(f'  - {active_count} trials in active follow-up phase')
    print(f'  - Patient enrollment competition is {"extremely high" if recruiting_count > 500 else "high"}')

    print(f'\n• Late-Stage Pipeline Maturity: {"VERY HIGH" if phase3_count > 30 else "HIGH" if phase3_count > 20 else "MODERATE"}')
    print(f'  - {phase3_count} active Phase 3 trials (near-term market entries)')
    print(f'  - {phase2_count} active Phase 2 trials (mid-term pipeline)')
    print(f'  - Phase 3/2 ratio: {phase3_count/phase2_count:.2f} ({"mature" if phase3_count/phase2_count > 0.5 else "developing"} pipeline)')

    print(f'\n• Industry vs Academic Activity:')
    print(f'  - Industry: {industry_count/total_active*100:.1f}% of active trials ({"HIGH" if industry_count/total_active > 0.4 else "MODERATE"} commercial focus)')
    print(f'  - Academic: {academic_count/total_active*100:.1f}% ({"exploratory research dominates" if academic_count/total_active > 0.6 else "balanced mix"})')

    print(f'\n• GLP-1 Market Dominance (Active Trials):')
    print(f'  - GLP-1 class: {glp1_count} active trials ({glp1_count/total_active*100:.1f}% of all active obesity trials)')
    print(f'  - Semaglutide: {sema_count} active trials ({"clear leader" if sema_count > glp1_count*0.4 else "strong player"})')
    print(f'  - Tirzepatide: {tirz_count} active trials ({"fast-growing challenger" if tirz_count > 50 else "emerging competitor"})')
    print(f'  - GLP-1 dominance: {"VERY HIGH" if glp1_count/total_active > 0.15 else "HIGH" if glp1_count/total_active > 0.10 else "MODERATE"}')

    print(f'\n• Near-Term Pipeline Velocity:')
    print(f'  - {pipeline_count} trials not yet recruiting (near-term pipeline additions)')
    print(f'  - Pipeline velocity: {"Accelerating" if pipeline_count > 100 else "Steady" if pipeline_count > 50 else "Slowing"}')
    print(f'  - Expected new trials: ~{pipeline_count} within next 6-12 months')

    print(f'\n• Competitive Intensity Score: {recruiting_count + phase3_count + (glp1_count/10):.0f}/1000')
    intensity = recruiting_count + phase3_count + (glp1_count/10)
    if intensity > 700:
        assessment = "EXTREMELY INTENSE - Saturated market, high barriers to differentiation"
    elif intensity > 500:
        assessment = "VERY INTENSE - Crowded field, differentiation critical"
    elif intensity > 300:
        assessment = "INTENSE - Competitive but opportunity for innovation"
    else:
        assessment = "MODERATE - Room for new entrants"
    print(f'  Assessment: {assessment}')

    print('\n' + '=' * 100)
    print('KEY TAKEAWAYS FOR COMPETITIVE STRATEGY')
    print('=' * 100)

    print(f'\n1. Patient Enrollment Competition:')
    print(f'   - {recruiting_count} trials competing for obesity patients')
    print(f'   - Enrollment speed critical for trial success')
    print(f'   - Consider novel patient populations or geographic expansion')

    print(f'\n2. GLP-1 Market Saturation:')
    print(f'   - {glp1_count} active GLP-1 trials indicate saturated mechanism')
    print(f'   - New GLP-1 programs need clear differentiation')
    print(f'   - Alternative mechanisms may offer white space')

    print(f'\n3. Industry Focus:')
    print(f'   - {industry_count} industry-sponsored active trials')
    print(f'   - {industry_count/total_active*100:.1f}% industry funding indicates {"strong" if industry_count/total_active > 0.3 else "moderate"} commercial confidence')

    print(f'\n4. Phase 3 Near-Term Competition:')
    print(f'   - {phase3_count} Phase 3 trials will report in next 1-3 years')
    print(f'   - These represent near-term competitive threats')
    print(f'   - Monitor closely for approval and market positioning')

    print('\n' + '=' * 100)
    print('ANALYSIS COMPLETE')
    print('=' * 100)

if __name__ == '__main__':
    main()
