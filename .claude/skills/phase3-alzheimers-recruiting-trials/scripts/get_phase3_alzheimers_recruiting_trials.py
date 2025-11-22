import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re
from collections import defaultdict


def get_phase3_alzheimers_recruiting_trials():
    """Get Phase 3 Alzheimer's disease trials recruiting globally.

    Handles multiple mechanisms of action and global trial sites.
    Uses pagination to retrieve complete dataset.

    Returns:
        dict: Contains total_count, trials_summary, and all_trials
    """
    trials = []
    page_token = None

    # CT.gov search with proper pagination
    while True:
        result = search(
            term="Alzheimer phase 3",
            status="RECRUITING",
            pageSize=100,
            pageToken=page_token
        )

        # Parse markdown response
        if isinstance(result, str):
            content = result
        else:
            content = str(result)

        # Extract NCT IDs and trial details from markdown
        # CT.gov markdown format: ### 1. NCT12345678
        nct_pattern = r'###\s+\d+\.\s+(NCT\d{8})'
        nct_matches = list(re.finditer(nct_pattern, content))

        if not nct_matches:
            # No more trials found
            break

        # Parse each trial block
        for i, match in enumerate(nct_matches):
            nct_id = match.group(1)

            # Get text until next trial or end
            start_pos = match.start()
            end_pos = nct_matches[i+1].start() if i+1 < len(nct_matches) else len(content)
            trial_block = content[start_pos:end_pos]

            # Extract fields using regex patterns
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', trial_block)
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial_block)
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', trial_block)

            # Extract intervention/mechanism (may not always be present)
            intervention_match = re.search(r'\*\*Intervention[s]?:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)', trial_block)

            # Extract locations (may span multiple lines)
            locations_match = re.search(r'\*\*Location[s]?:\*\*\s*(.+?)(?:\n\*\*|$)', trial_block, re.DOTALL)

            # Safety checks and extraction
            phase = phase_match.group(1).strip() if phase_match else "Unknown"
            status = status_match.group(1).strip() if status_match else "Unknown"

            # Only include Phase 3 RECRUITING trials
            if "Phase 3" not in phase or "RECRUITING" not in status.upper():
                continue

            title = title_match.group(1).strip() if title_match else "Unknown"
            mechanism = intervention_match.group(1).strip() if intervention_match else "Not specified"
            locations = locations_match.group(1).strip() if locations_match else "Global"

            # Clean up mechanism text (remove line breaks, truncate long values)
            mechanism = re.sub(r'\s+', ' ', mechanism)[:150]

            trials.append({
                'nct_id': nct_id,
                'title': title[:100],
                'phase': phase,
                'mechanism': mechanism,
                'locations': locations[:200]
            })

        # Check for pagination token in response
        token_match = re.search(r'"pageToken"\s*:\s*"([^"]+)"', content)
        if token_match:
            page_token = token_match.group(1)
        else:
            # No next page
            break

    # Remove duplicates (keep insertion order)
    seen = set()
    unique_trials = []
    for trial in trials:
        if trial['nct_id'] not in seen:
            seen.add(trial['nct_id'])
            unique_trials.append(trial)

    trials = unique_trials
    total_count = len(trials)

    # Aggregate statistics and categorize mechanisms
    mechanism_counts = defaultdict(int)
    for trial in trials:
        mech = trial['mechanism'].lower()
        if 'amyloid' in mech:
            mechanism_counts['Anti-Amyloid'] += 1
        elif 'tau' in mech:
            mechanism_counts['Anti-Tau'] += 1
        elif 'nasal' in mech or 'intranasal' in mech:
            mechanism_counts['Intranasal'] += 1
        elif 'vaccine' in mech:
            mechanism_counts['Immunotherapy/Vaccine'] += 1
        elif 'neuroinflammation' in mech or 'inflammation' in mech:
            mechanism_counts['Anti-Neuroinflammation'] += 1
        elif 'biomarker' in mech:
            mechanism_counts['Biomarker-Guided'] += 1
        elif 'gene' in mech:
            mechanism_counts['Gene Therapy'] += 1
        else:
            mechanism_counts['Other/Combination'] += 1

    summary = {
        'total_recruiting_phase3_trials': total_count,
        'scope': 'Global',
        'mechanism_diversity': dict(sorted(mechanism_counts.items(), key=lambda x: x[1], reverse=True)),
        'top_trials': trials[:15] if trials else []
    }

    return {
        'total_count': total_count,
        'trials_summary': summary,
        'all_trials': trials
    }


if __name__ == "__main__":
    result = get_phase3_alzheimers_recruiting_trials()

    print("\n" + "="*80)
    print("PHASE 3 ALZHEIMER'S DISEASE TRIALS - RECRUITING GLOBALLY")
    print("="*80)

    summary = result['trials_summary']
    print(f"\nTotal Recruiting Phase 3 Trials: {summary['total_recruiting_phase3_trials']}")
    print(f"Geographic Scope: {summary['scope']}")

    print(f"\nMechanism of Action Diversity:")
    for mechanism, count in summary['mechanism_diversity'].items():
        pct = (count / summary['total_recruiting_phase3_trials'] * 100) if summary['total_recruiting_phase3_trials'] > 0 else 0
        print(f"  • {mechanism}: {count} trials ({pct:.1f}%)")

    print(f"\nTop 15 Recruiting Trials:")
    for i, trial in enumerate(summary['top_trials'], 1):
        print(f"\n  {i}. {trial['nct_id']}")
        print(f"     Title: {trial['title']}")
        print(f"     Mechanism: {trial['mechanism']}")
        print(f"     Locations: {trial['locations'][:80]}...")
