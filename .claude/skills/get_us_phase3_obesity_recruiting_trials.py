import sys
import re
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_us_phase3_obesity_recruiting_trials():
    """Get count of Phase 3 obesity trials actively recruiting in the US."""
    result = search(
        condition="obesity",
        phase="PHASE3",
        status="recruiting",
        location="United States",
        pageSize=10
    )

    # CT.gov returns MARKDOWN string - parse with regex
    if isinstance(result, str):
        match = re.search(r'\*\*Results:\*\* \d+ of (\d+) studies found', result)
        if match:
            return int(match.group(1))

    return 0
