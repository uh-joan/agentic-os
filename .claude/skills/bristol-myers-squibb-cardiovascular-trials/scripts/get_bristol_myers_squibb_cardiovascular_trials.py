import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re

def get_bristol_myers_squibb_cardiovascular_trials():
    """Get Bristol Myers Squibb cardiovascular clinical trials across all phases.

    Uses pagination to retrieve complete dataset from ClinicalTrials.gov.
    Searches for trials sponsored by Bristol Myers Squibb with cardiovascular conditions.

    Returns:
        dict: Contains total_count, trials data, and status/phase summary
    """

    all_trials = []
    page_token = None
    page_count = 0

    print("Fetching Bristol Myers Squibb cardiovascular trials from ClinicalTrials.gov...")

    # Pagination loop - critical for complete data retrieval
    while True:
        page_count += 1
        print(f"  Fetching page {page_count}...")

        # Call CT.gov search with pagination
        # Search for Bristol Myers Squibb cardiovascular trials
        if page_token:
            result = search(
                query="Bristol Myers Squibb cardiovascular",
                pageSize=1000,
                pageToken=page_token
            )
        else:
            result = search(
                query="Bristol Myers Squibb cardiovascular",
                pageSize=1000
            )

        # CT.gov returns markdown - extract trial blocks
        trials_text = result if isinstance(result, str) else str(result)

        # Split trials by NCT ID headers (markdown format)
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', trials_text)

        # Skip first block (header/metadata)
        if len(trial_blocks) > 1:
            all_trials.extend(trial_blocks[1:])

        # Check for next page token
        next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', trials_text)

        if next_token_match:
            page_token = next_token_match.group(1)
            print(f"    Found {len(trial_blocks)-1} trials, continuing to next page...")
        else:
            print(f"    Found {len(trial_blocks)-1} trials, no more pages.")
            break

    total_count = len(all_trials)

    # Parse status distribution
    status_counts = {}
    for trial in all_trials:
        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', trial)
        if status_match:
            status = status_match.group(1).strip()
            status_counts[status] = status_counts.get(status, 0) + 1

    # Parse phase distribution
    phase_counts = {}
    for trial in all_trials:
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial)
        if phase_match:
            phase = phase_match.group(1).strip()
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

    # Sort by frequency
    sorted_statuses = sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_phases = sorted(phase_counts.items(), key=lambda x: x[1], reverse=True)

    summary = {
        'total_count': total_count,
        'status_distribution': dict(sorted_statuses),
        'phase_distribution': dict(sorted_phases),
        'pages_fetched': page_count
    }

    return {
        'total_count': total_count,
        'trials': all_trials,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_bristol_myers_squibb_cardiovascular_trials()

    print(f"\n{'='*60}")
    print(f"Bristol Myers Squibb Cardiovascular Trials Summary")
    print(f"{'='*60}")
    print(f"Total trials found: {result['summary']['total_count']}")
    print(f"Pages fetched: {result['summary']['pages_fetched']}")
    print(f"\nStatus Distribution:")
    for status, count in result['summary']['status_distribution'].items():
        print(f"  {status}: {count}")
    print(f"\nPhase Distribution:")
    for phase, count in result['summary']['phase_distribution'].items():
        print(f"  {phase}: {count}")
    print(f"{'='*60}\n")
