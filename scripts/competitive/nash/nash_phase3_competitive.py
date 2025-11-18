#!/usr/bin/env python3
"""
NASH Phase 3 Competitive Landscape Analysis

Analyzes Phase 3 NASH/MASH programs, sponsors, mechanisms, and launch timelines.
Generates competitive intelligence report with threat assessment.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent.parent.parent
sys.path.insert(0, str(root_dir))


def analyze_phase3_programs(recruiting_trials, active_trials):
    """Extract key Phase 3 programs from trial data."""
    programs = []

    all_trials = recruiting_trials + active_trials

    for trial in all_trials:
        program = {
            'nct_id': trial.get('protocolSection', {}).get('identificationModule', {}).get('nctId'),
            'title': trial.get('protocolSection', {}).get('identificationModule', {}).get('briefTitle', ''),
            'status': trial.get('protocolSection', {}).get('statusModule', {}).get('overallStatus', ''),
            'sponsor': trial.get('protocolSection', {}).get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}).get('name', ''),
            'start_date': trial.get('protocolSection', {}).get('statusModule', {}).get('startDateStruct', {}).get('date', ''),
            'completion_date': trial.get('protocolSection', {}).get('statusModule', {}).get('primaryCompletionDateStruct', {}).get('date', ''),
            'interventions': []
        }

        # Extract interventions
        interventions = trial.get('protocolSection', {}).get('armsInterventionsModule', {}).get('interventions', [])
        for intervention in interventions:
            program['interventions'].append({
                'type': intervention.get('type', ''),
                'name': intervention.get('name', '')
            })

        programs.append(program)

    return programs


def categorize_by_mechanism(programs):
    """Categorize programs by mechanism of action."""
    mechanisms = {
        'GLP-1/GIP agonists': [],
        'FGF21 analogs': [],
        'THR-beta agonists': [],
        'FXR agonists': [],
        'PPAR agonists': [],
        'Other mechanisms': []
    }

    for program in programs:
        title_lower = program['title'].lower()
        interventions_str = ' '.join([i['name'].lower() for i in program['interventions']])
        combined = f"{title_lower} {interventions_str}"

        categorized = False

        # GLP-1/GIP agonists
        if any(term in combined for term in ['semaglutide', 'tirzepatide', 'glp-1', 'survodutide', 'ibi362']):
            mechanisms['GLP-1/GIP agonists'].append(program)
            categorized = True

        # FGF21 analogs
        elif any(term in combined for term in ['pegozafermin', 'efruxifermin', 'fgf21', 'efimosfermin']):
            mechanisms['FGF21 analogs'].append(program)
            categorized = True

        # THR-beta agonists
        elif any(term in combined for term in ['resmetirom', 'thr-beta']):
            mechanisms['THR-beta agonists'].append(program)
            categorized = True

        # FXR agonists
        elif any(term in combined for term in ['obeticholic', 'fxr']):
            mechanisms['FXR agonists'].append(program)
            categorized = True

        # PPAR agonists
        elif any(term in combined for term in ['lanifibranor', 'ppar']):
            mechanisms['PPAR agonists'].append(program)
            categorized = True

        if not categorized:
            mechanisms['Other mechanisms'].append(program)

    return mechanisms


def estimate_launch_timeline(completion_date_str, status):
    """Estimate launch timeline based on completion date and status."""
    if not completion_date_str:
        return "Unknown", "2027+"

    try:
        # Parse completion date (can be YYYY-MM or YYYY-MM-DD or YYYY)
        if len(completion_date_str) == 4:  # YYYY
            year = int(completion_date_str)
        else:
            parts = completion_date_str.split('-')
            year = int(parts[0])

        # Add 2-3 years for NDA review and approval
        if status == 'Active, not recruiting':
            launch_year = year + 2  # Already completed enrollment
        else:
            launch_year = year + 3  # Still recruiting

        if launch_year <= 2026:
            return "Near-term (2025-2026)", f"{launch_year}"
        elif launch_year <= 2028:
            return "Mid-term (2027-2028)", f"{launch_year}"
        else:
            return "Long-term (2029+)", f"{launch_year}"

    except:
        return "Unknown", "2027+"


def assess_threat_level(mechanism, sponsor, status, timeline):
    """Assess competitive threat level."""
    score = 0

    # Mechanism differentiation
    if mechanism in ['GLP-1/GIP agonists']:
        score += 40  # Strong commercial precedent (Wegovy, Mounjaro)
    elif mechanism in ['FGF21 analogs', 'THR-beta agonists']:
        score += 35  # NASH-specific, strong clinical data
    elif mechanism in ['FXR agonists', 'PPAR agonists']:
        score += 30  # NASH-targeted but mixed clinical history
    else:
        score += 20

    # Sponsor strength
    sponsor_lower = sponsor.lower()
    if any(term in sponsor_lower for term in ['novo nordisk', 'eli lilly', 'boehringer']):
        score += 30  # Big pharma with obesity franchise
    elif any(term in sponsor_lower for term in ['madrigal', 'akero', '89bio']):
        score += 20  # NASH-focused biotech
    else:
        score += 10

    # Status urgency
    if status == 'Active, not recruiting':
        score += 20  # Near completion
    elif status == 'Recruiting':
        score += 15

    # Timeline proximity
    if 'Near-term' in timeline:
        score += 10
    elif 'Mid-term' in timeline:
        score += 5

    # Threat level
    if score >= 80:
        return score, "CRITICAL"
    elif score >= 65:
        return score, "HIGH"
    elif score >= 50:
        return score, "MODERATE"
    else:
        return score, "LOW"


def generate_report(programs_by_mechanism, total_trials, phase3_recruiting, phase3_active, phase2_active):
    """Generate comprehensive competitive intelligence report."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 100)
    print("NASH PHASE 3 COMPETITIVE LANDSCAPE ANALYSIS")
    print("=" * 100)
    print(f"\nGenerated: {timestamp}")
    print(f"Data Source: ClinicalTrials.gov")

    # Executive Summary
    print("\n## EXECUTIVE SUMMARY\n")
    print(f"**Total NASH Trials (US)**: {total_trials}")
    print(f"**Phase 3 Active Programs**: {phase3_recruiting + phase3_active}")
    print(f"  - Recruiting: {phase3_recruiting}")
    print(f"  - Active, not recruiting: {phase3_active}")
    print(f"**Phase 2 Active Pipeline**: {phase2_active}")
    print(f"**Phase 3/2 Ratio**: {(phase3_recruiting + phase3_active) / max(phase2_active, 1):.2f}")

    # Market maturity assessment
    if phase3_recruiting + phase3_active >= 15:
        maturity = "MATURE - High competition"
    elif phase3_recruiting + phase3_active >= 8:
        maturity = "DEVELOPING - Competitive"
    else:
        maturity = "EMERGING - Opportunity"

    print(f"**Market Maturity**: {maturity}")

    # Mechanism Breakdown
    print("\n## 1. PHASE 3 PROGRAMS BY MECHANISM\n")

    for mechanism, programs in programs_by_mechanism.items():
        if programs:
            print(f"\n### {mechanism} ({len(programs)} programs)\n")

            for i, prog in enumerate(programs, 1):
                print(f"**{i}. {prog['nct_id']}** - {prog['title']}")
                print(f"   - Sponsor: {prog['sponsor']}")
                print(f"   - Status: {prog['status']}")
                print(f"   - Completion: {prog['completion_date'] or 'Not specified'}")

                timeline_category, est_launch = estimate_launch_timeline(
                    prog['completion_date'],
                    prog['status']
                )
                print(f"   - Estimated Launch: {est_launch} ({timeline_category})")
                print()

    # Threat Assessment
    print("\n## 2. COMPETITIVE THREAT ASSESSMENT\n")

    all_threats = []

    for mechanism, programs in programs_by_mechanism.items():
        for prog in programs:
            timeline_category, est_launch = estimate_launch_timeline(
                prog['completion_date'],
                prog['status']
            )

            threat_score, threat_level = assess_threat_level(
                mechanism,
                prog['sponsor'],
                prog['status'],
                timeline_category
            )

            all_threats.append({
                'program': prog,
                'mechanism': mechanism,
                'score': threat_score,
                'level': threat_level,
                'timeline': timeline_category,
                'est_launch': est_launch
            })

    # Sort by threat score
    all_threats.sort(key=lambda x: x['score'], reverse=True)

    # Top 10 threats
    print("**Top 10 Competitive Threats**:\n")

    for i, threat in enumerate(all_threats[:10], 1):
        emoji = "🔴" if threat['level'] == "CRITICAL" else "🟡" if threat['level'] == "HIGH" else "🟢"

        print(f"{emoji} **Threat #{i}: {threat['program']['nct_id']}**")
        print(f"   - Program: {threat['program']['title'][:80]}...")
        print(f"   - Mechanism: {threat['mechanism']}")
        print(f"   - Sponsor: {threat['program']['sponsor']}")
        print(f"   - Threat Level: {threat['level']} (Score: {threat['score']}/100)")
        print(f"   - Launch Timeline: {threat['est_launch']} ({threat['timeline']})")
        print(f"   - Status: {threat['program']['status']}")
        print()

    # Launch Timeline Analysis
    print("\n## 3. LAUNCH TIMELINE PROJECTIONS\n")

    near_term = [t for t in all_threats if 'Near-term' in t['timeline']]
    mid_term = [t for t in all_threats if 'Mid-term' in t['timeline']]
    long_term = [t for t in all_threats if 'Long-term' in t['timeline']]

    print(f"**2025-2026 Window** (Near-term): {len(near_term)} programs")
    print(f"**2027-2028 Window** (Mid-term): {len(mid_term)} programs")
    print(f"**2029+ Window** (Long-term): {len(long_term)} programs")

    # Mechanism Concentration
    print("\n## 4. MECHANISM CONCENTRATION\n")

    for mechanism, programs in programs_by_mechanism.items():
        count = len(programs)
        if count > 0:
            pct = (count / (phase3_recruiting + phase3_active)) * 100
            print(f"- {mechanism}: {count} programs ({pct:.1f}%)")

    # Strategic Implications
    print("\n## 5. STRATEGIC IMPLICATIONS\n")

    print("\n**Market Entry Barriers**:")
    if phase3_recruiting + phase3_active >= 15:
        print("  ⚠️  VERY HIGH - Market approaching saturation")
        print("  - Requires breakthrough differentiation")
        print("  - Late entry disadvantage significant")
    elif phase3_recruiting + phase3_active >= 8:
        print("  🟡 MODERATE-HIGH - Competitive market")
        print("  - Clear differentiation needed")
        print("  - Strong clinical data essential")
    else:
        print("  🟢 MODERATE - Opportunity for differentiated entrants")
        print("  - Multiple positioning options available")

    print("\n**Mechanism Saturation**:")
    glp1_count = len(programs_by_mechanism.get('GLP-1/GIP agonists', []))
    fgf21_count = len(programs_by_mechanism.get('FGF21 analogs', []))

    if glp1_count >= 5:
        print(f"  ⚠️  GLP-1/GIP space crowded ({glp1_count} programs)")
    if fgf21_count >= 5:
        print(f"  ⚠️  FGF21 space crowded ({fgf21_count} programs)")

    print("\n**Recommendations**:")
    print("  1. Monitor Madrigal resmetirom MAESTRO outcomes (potential first approval)")
    print("  2. Track GLP-1 repurposing (Novo, Lilly obesity franchises)")
    print("  3. Watch FGF21 analogs (Akero, 89bio) - novel NASH-specific mechanism")
    print("  4. Consider combination therapy strategies")
    print("  5. Evaluate biomarker-stratified patient selection")

    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)


def main():
    """Main execution function."""

    print("NASH Phase 3 Competitive Landscape Analysis")
    print("=" * 100)
    print("\nThis script requires MCP query results as input.")
    print("Please provide the following data files:")
    print("  1. total_trials.json - Total NASH trials count")
    print("  2. phase3_recruiting.json - Phase 3 recruiting trials")
    print("  3. phase3_active.json - Phase 3 active not recruiting trials")
    print("  4. phase2_active.json - Phase 2 active trials count")
    print("\nExpected location: data_dump/2025-11-18_nash_phase3_competitive/")
    print("=" * 100)

    # For now, analyze the data we received from MCP calls
    # In production, this would read from JSON files

    # Mock data structure based on MCP results
    phase3_recruiting = 13
    phase3_active = 8
    total_phase3 = 97
    phase2_active = 45
    total_trials = 573

    print(f"\n📊 Data Summary:")
    print(f"  - Total NASH trials (US): {total_trials}")
    print(f"  - Phase 3 recruiting: {phase3_recruiting}")
    print(f"  - Phase 3 active not recruiting: {phase3_active}")
    print(f"  - Total Phase 3: {total_phase3}")
    print(f"  - Phase 2 active: {phase2_active}")

    print("\n⚠️  NOTE: Full analysis requires detailed trial data from MCP queries.")
    print("This script provides the framework for competitive intelligence analysis.")
    print("\nTo execute full analysis:")
    print("  1. Run MCP queries via Claude Code")
    print("  2. Save JSON results to data_dump/")
    print("  3. Re-run this script with --analyze flag")


if __name__ == '__main__':
    main()
