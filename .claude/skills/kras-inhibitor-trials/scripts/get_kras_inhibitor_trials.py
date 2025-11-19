import sys
import re
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_kras_inhibitor_trials():
    """Get KRAS inhibitor clinical trials across all phases.

    Returns:
        dict: Contains:
            - total_count (int): Total number of trials found
            - trials_summary (str): Markdown-formatted summary of trials

    Raises:
        ValueError: If no trials found or data validation fails
        TypeError: If response format is invalid
    """
    result = search(
        term="KRAS inhibitor",
        pageSize=100
    )

    # Validate response exists
    if not result:
        raise ValueError("No data returned from CT.gov API")

    # CT.gov returns MARKDOWN string - validate type
    if not isinstance(result, str):
        raise TypeError(f"Expected markdown string from CT.gov, got {type(result)}")

    # Validate response has content
    if len(result) < 100:
        raise ValueError("CT.gov returned insufficient data - check search term")

    # Extract total count
    count_match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', result)
    if not count_match:
        raise ValueError("Could not parse trial count from CT.gov response")

    total_count = int(count_match.group(1))

    # Validate count > 0
    if total_count == 0:
        raise ValueError("No KRAS inhibitor trials found - check search term")

    return {
        'total_count': total_count,
        'trials_summary': result
    }

if __name__ == "__main__":
    try:
        result = get_kras_inhibitor_trials()
        print(f"✓ Data collection successful: {result['total_count']} trials found")
        print()
        print(result['trials_summary'])
    except (ValueError, TypeError) as e:
        print(f"✗ Data validation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)
