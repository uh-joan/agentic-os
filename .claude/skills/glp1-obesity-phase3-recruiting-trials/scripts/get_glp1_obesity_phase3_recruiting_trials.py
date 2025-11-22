import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_glp1_obesity_phase3_recruiting_trials():
    """Get Phase 3 obesity trials using GLP-1 agonists currently recruiting in the US.

    Returns:
        dict: Contains total_count, data, and summary
    """
    all_trials = []
    page_token = None

    # Pagination loop to get all results
    while True:
        # Query parameters
        params = {
            "query.term": "obesity GLP-1 agonist",
            "filter.overallStatus": "RECRUITING",
            "filter.phase": "PHASE3",
            "filter.geo": "distance(39.8,-98.6,2000mi)",  # US center point with 2000mi radius
            "pageSize": 1000
        }

        if page_token:
            params["pageToken"] = page_token

        result = search(**params)

        # Parse markdown response
        import re

        # Split trials by NCT ID headers
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:  # Skip first empty block
            trial = {}

            # Extract NCT ID from block
            nct_match = re.search(r'NCT\d{8}', block)
            if nct_match:
                trial['nct_id'] = nct_match.group()

            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
            if title_match:
                trial['title'] = title_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', block)
            if status_match:
                trial['status'] = status_match.group(1).strip()

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', block)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()

            # Extract locations
            locations_match = re.search(r'\*\*Locations:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', block, re.DOTALL)
            if locations_match:
                trial['locations'] = locations_match.group(1).strip()

            if trial:
                all_trials.append(trial)

        # Check for next page token
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            page_token = next_token_match.group(1)
        else:
            break

    # Create summary
    summary = {
        'total_trials': len(all_trials),
        'query_parameters': {
            'disease': 'Obesity',
            'intervention': 'GLP-1 agonist',
            'phase': 'Phase 3',
            'status': 'Recruiting',
            'geography': 'United States'
        }
    }

    return {
        'total_count': len(all_trials),
        'data': all_trials,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_glp1_obesity_phase3_recruiting_trials()
    print(f"\nTotal Phase 3 obesity trials using GLP-1 agonists recruiting in US: {result['total_count']}")
    print(f"\nQuery Parameters:")
    for key, value in result['summary']['query_parameters'].items():
        print(f"  {key}: {value}")

    if result['total_count'] > 0:
        print(f"\nSample trials (first 5):")
        for i, trial in enumerate(result['data'][:5], 1):
            print(f"\n{i}. {trial.get('nct_id', 'N/A')}")
            print(f"   Title: {trial.get('title', 'N/A')[:100]}...")
            print(f"   Phase: {trial.get('phase', 'N/A')}")
            print(f"   Status: {trial.get('status', 'N/A')}")
