import sys
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search
import re

def get_rheumatoid_arthritis_trials():
    """Get all rheumatoid arthritis clinical trials from ClinicalTrials.gov.

    Uses pagination to retrieve complete dataset.

    Returns:
        dict: Contains total_count and trials_summary
    """
    all_trials = []
    page_token = None
    page_num = 1

    print(f"Fetching rheumatoid arthritis trials (this may take a moment)...")

    while True:
        print(f"  Fetching page {page_num}...", end=" ", flush=True)

        # Make API call with pagination
        if page_token:
            result = search(
                term="rheumatoid arthritis",
                pageSize=1000,
                pageToken=page_token
            )
        else:
            result = search(
                term="rheumatoid arthritis",
                pageSize=1000
            )

        # CT.gov returns markdown - extract trial count from header
        count_match = re.search(r'\*\*Results:\*\* \d+ of ([\d,]+) studies found', result)
        if count_match and page_num == 1:
            total_available = int(count_match.group(1).replace(',', ''))
            print(f"(Total available: {total_available})")
        else:
            print()

        # Extract trials from markdown sections (numbered format)
        trials = re.findall(r'### \d+\. (NCT\d+)\n\*\*Title:\*\* (.*?)\n(.*?)(?=\n### \d+\.|\Z)', result, re.DOTALL)

        if not trials:
            print(f"  No more trials found on page {page_num}")
            break

        all_trials.extend(trials)
        print(f"  Retrieved {len(trials)} trials (Total so far: {len(all_trials)})")

        # Check for next page token
        token_match = re.search(r'pageToken: "([^"]+)"', result)
        if token_match:
            page_token = token_match.group(1)
            page_num += 1
        else:
            print(f"  No more pages")
            break

    # Format summary
    summary = f"# Rheumatoid Arthritis Clinical Trials\n\n"
    summary += f"**Total trials found: {len(all_trials)}**\n\n"

    # Add sample trials
    summary += "## Sample Trials (First 10):\n\n"
    for nct_id, title, details in all_trials[:10]:
        summary += f"### {nct_id}: {title}\n{details.strip()}\n\n"

    return {
        'total_count': len(all_trials),
        'trials_summary': summary
    }

if __name__ == "__main__":
    result = get_rheumatoid_arthritis_trials()
    print(result['trials_summary'])
