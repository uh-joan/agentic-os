import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_alk_rearrangement_trials():
    """Get ALK rearrangement positive cancer clinical trials.

    Searches for ALK-positive, ALK fusion, ALK rearrangement trials.
    Primarily NSCLC but may include other ALK+ cancers.

    Note: Basic search results only include NCT ID, Title, Status, Posted Date.
    For detailed info (phase, sponsor, enrollment), individual trial lookups needed.

    Returns:
        dict: Contains:
            - total_count (int): Total number of trials found
            - trials (list): Parsed trial data
            - status_distribution (dict): Status breakdown
    """
    # Search for ALK rearrangement trials with comprehensive terminology
    result = search(
        term="ALK rearrangement OR ALK fusion OR ALK positive OR ALK inhibitor",
        pageSize=100
    )

    # Validate response exists
    if not result or not isinstance(result, str):
        return {'total_count': 0, 'trials': [], 'status_distribution': {}}

    # Extract total count
    count_match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', result)
    total_count = int(count_match.group(1)) if count_match else 0

    # Parse trials from markdown
    trials = []
    status_counts = {}

    trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

    for block in trial_blocks[1:]:  # Skip first empty block
        # Extract NCT ID
        nct_match = re.search(r'NCT\d{8}', block)
        if not nct_match:
            continue

        trial_data = {'nct_id': nct_match.group()}

        # Extract available fields from basic search
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
        trial_data['title'] = title_match.group(1).strip() if title_match else 'Unknown'

        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', block)
        trial_data['status'] = status_match.group(1).strip() if status_match else 'Unknown'

        posted_match = re.search(r'\*\*Posted:\*\*\s*(.+?)(?:\n|$)', block)
        trial_data['posted_date'] = posted_match.group(1).strip() if posted_match else 'Unknown'

        link_match = re.search(r'\[View Study\]\((https://clinicaltrials\.gov/study/NCT\d{8})\)', block)
        trial_data['link'] = link_match.group(1) if link_match else f"https://clinicaltrials.gov/study/{trial_data['nct_id']}"

        trials.append(trial_data)

        # Count statuses
        status = trial_data['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        'total_count': total_count,
        'trials': trials,
        'status_distribution': status_counts
    }

if __name__ == "__main__":
    result = get_alk_rearrangement_trials()

    print(f"\nALK Rearrangement Positive Cancer Trials Summary")
    print("=" * 60)
    print(f"Total trials: {result['total_count']}")
    print(f"Trials retrieved: {len(result['trials'])}")
    print(f"\nNote: Basic search results include NCT ID, Title, Status, Posted Date.")
    print(f"For detailed info (phase, sponsor, enrollment), individual lookups needed.\n")

    if result['status_distribution']:
        print("Status Distribution:")
        for status, count in sorted(result['status_distribution'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(result['trials']) * 100) if result['trials'] else 0
            print(f"  {status}: {count} ({pct:.1f}%)")

    print(f"\nSample Trials (first 10):")
    for i, t in enumerate(result['trials'][:10], 1):
        print(f"\n{i}. {t['nct_id']}")
        print(f"   Title: {t['title']}")
        print(f"   Status: {t['status']}")
        print(f"   Posted: {t['posted_date']}")
        print(f"   Link: {t['link']}")
