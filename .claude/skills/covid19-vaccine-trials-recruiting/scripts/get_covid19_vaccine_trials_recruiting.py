"""
Query ClinicalTrials.gov for active COVID-19 vaccine trials currently recruiting globally.

This skill demonstrates:
- CT.gov MCP server integration
- Markdown response parsing
- Multi-field data extraction
- Statistical aggregation (phases, sponsors, countries)
"""

import sys
import re
from pathlib import Path

# Import MCP CT.gov server
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "mcp"))
from servers.ct_gov_mcp import ct_gov_studies

def get_covid19_vaccine_trials_recruiting():
    """
    Query ClinicalTrials.gov for active COVID-19 vaccine trials currently recruiting globally.

    Returns:
        dict: Summary of findings including:
            - total_trials: Total number of recruiting trials
            - trials: List of trial dictionaries with details
            - phase_distribution: Count of trials by phase
            - top_sponsors: Top sponsors and their trial counts
            - countries_count: Number of unique countries
            - unique_countries: List of all countries involved

    Example:
        >>> results = get_covid19_vaccine_trials_recruiting()
        >>> print(f"Found {results['total_trials']} trials")
        >>> print(f"Phase 3 trials: {results['phase_distribution'].get('Phase 3', 0)}")
    """
    # Query CT.gov for COVID-19 vaccine trials that are recruiting
    response = ct_gov_studies(
        condition="COVID-19",
        intervention="vaccine",
        status="RECRUITING",
        fields="NCTId,BriefTitle,OverallStatus,Phase,LeadSponsorName,LocationCountry,StudyType,EnrollmentCount"
    )

    # Parse markdown response
    lines = response.split('\n')

    trials = []
    current_trial = {}

    for line in lines:
        line = line.strip()

        if line.startswith('**NCT Number:**'):
            if current_trial:
                trials.append(current_trial)
            current_trial = {'nct_id': line.split('**NCT Number:**')[1].strip()}

        elif line.startswith('**Title:**'):
            current_trial['title'] = line.split('**Title:**')[1].strip()

        elif line.startswith('**Status:**'):
            current_trial['status'] = line.split('**Status:**')[1].strip()

        elif line.startswith('**Phase:**'):
            current_trial['phase'] = line.split('**Phase:**')[1].strip()

        elif line.startswith('**Sponsor:**'):
            current_trial['sponsor'] = line.split('**Sponsor:**')[1].strip()

        elif line.startswith('**Countries:**'):
            current_trial['countries'] = line.split('**Countries:**')[1].strip()

        elif line.startswith('**Study Type:**'):
            current_trial['study_type'] = line.split('**Study Type:**')[1].strip()

        elif line.startswith('**Enrollment:**'):
            enrollment_text = line.split('**Enrollment:**')[1].strip()
            current_trial['enrollment'] = enrollment_text

    # Add last trial
    if current_trial:
        trials.append(current_trial)

    # Analyze data
    total_trials = len(trials)

    # Count by phase
    phase_counts = {}
    for trial in trials:
        phase = trial.get('phase', 'Not Specified')
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    # Count by sponsor
    sponsor_counts = {}
    for trial in trials:
        sponsor = trial.get('sponsor', 'Unknown')
        sponsor_counts[sponsor] = sponsor_counts.get(sponsor, 0) + 1

    # Get unique countries
    all_countries = set()
    for trial in trials:
        countries_str = trial.get('countries', '')
        if countries_str:
            countries = [c.strip() for c in countries_str.split(',')]
            all_countries.update(countries)

    return {
        'total_trials': total_trials,
        'trials': trials,
        'phase_distribution': phase_counts,
        'top_sponsors': dict(sorted(sponsor_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        'countries_count': len(all_countries),
        'unique_countries': sorted(list(all_countries))
    }


if __name__ == "__main__":
    # Example usage
    results = get_covid19_vaccine_trials_recruiting()

    print("=" * 80)
    print("COVID-19 VACCINE TRIALS - CURRENTLY RECRUITING (GLOBAL)")
    print("=" * 80)
    print(f"\nTotal Active Recruiting Trials: {results['total_trials']}")

    print("\n--- PHASE DISTRIBUTION ---")
    for phase, count in sorted(results['phase_distribution'].items()):
        print(f"  {phase}: {count} trials")

    print("\n--- TOP 10 SPONSORS ---")
    for sponsor, count in list(results['top_sponsors'].items())[:10]:
        print(f"  {sponsor}: {count} trial(s)")

    print(f"\n--- GEOGRAPHIC REACH ---")
    print(f"Total Countries: {results['countries_count']}")
    print(f"Countries: {', '.join(results['unique_countries'][:20])}")
    if results['countries_count'] > 20:
        print(f"  ... and {results['countries_count'] - 20} more")

    print("\n--- SAMPLE TRIALS ---")
    for trial in results['trials'][:5]:
        print(f"\n{trial.get('nct_id', 'N/A')}: {trial.get('title', 'No title')[:80]}")
        print(f"  Phase: {trial.get('phase', 'N/A')} | Sponsor: {trial.get('sponsor', 'N/A')}")
        print(f"  Countries: {trial.get('countries', 'N/A')[:100]}")

    if results['total_trials'] > 5:
        print(f"\n... and {results['total_trials'] - 5} more trials")

    print("\n" + "=" * 80)
