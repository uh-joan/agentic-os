import sys
import re
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_braf_inhibitor_trials():
    """Get BRAF inhibitor clinical trials across all phases.

    Handles pagination to retrieve all results (not limited to first 1000).

    Returns:
        dict: Contains total_count and trials_summary (markdown string)
    """
    all_results = []
    page_size = 1000
    page_token = None

    # First request to get total count and first page
    result = search(term="BRAF inhibitor", pageSize=page_size)

    # Extract total count from markdown
    count_match = re.search(r'\*\*Results:\*\* (\d+) of (\d+) studies found', result)
    if not count_match:
        return {'total_count': 0, 'trials_summary': result}

    total_count = int(count_match.group(2))
    all_results.append(result)

    # Extract pageToken if present
    token_match = re.search(r'Next page token: `([^`]+)`', result)
    if token_match:
        page_token = token_match.group(1)

    # Keep fetching pages until we have all results
    fetched_count = min(page_size, total_count)

    while page_token and fetched_count < total_count:
        result = search(
            term="BRAF inhibitor",
            pageSize=page_size,
            pageToken=page_token
        )
        all_results.append(result)

        # Update fetched count
        fetched_count += page_size

        # Check for next page token
        token_match = re.search(r'Next page token: `([^`]+)`', result)
        if token_match:
            page_token = token_match.group(1)
        else:
            page_token = None

    # Combine all results
    combined_summary = "\n\n---\n\n".join(all_results)

    return {
        'total_count': total_count,
        'trials_summary': combined_summary
    }

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    result = get_braf_inhibitor_trials()
    print(f"Total BRAF inhibitor trials found: {result['total_count']}")
    print("\nTrials summary:")
    print(result['trials_summary'])
