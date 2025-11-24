import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_clinical_trials(term, phase=None):
    """Get clinical trials for ANY therapeutic area, drug, or condition.

    Generic skill that replaces 20+ therapeutic-area-specific skills.
    Uses the same pattern as get_company_segment_geographic_financials(ticker, quarters=8).

    Args:
        term (str): Search term - therapeutic area, drug class, or condition
                   Examples: "GLP-1", "KRAS inhibitor", "Alzheimer's disease",
                   "heart failure", "obesity", "diabetes"
        phase (str, optional): Trial phase filter - "PHASE1", "PHASE2", "PHASE3", "PHASE4"
                              If None, returns all phases. Defaults to None.

    Returns:
        dict: {
            'total_count': int,           # Total trials in database
            'trials_parsed': list,        # List of trial objects
            'summary': {
                'total_trials': int,
                'trials_retrieved': int,
                'pages_fetched': int,
                'retrieval_note': str,
                'status_breakdown': dict,
                'phase_breakdown': dict
            }
        }

    Examples:
        # Basic search (all phases)
        >>> result = get_clinical_trials("GLP-1")
        >>> result = get_clinical_trials("KRAS inhibitor")

        # Phase-filtered search
        >>> result = get_clinical_trials("heart failure", phase="PHASE3")
        >>> result = get_clinical_trials("obesity", phase="PHASE2")
    """

    print(f"\n{'='*80}")
    print(f"CLINICAL TRIALS SEARCH")
    print(f"{'='*80}")
    print(f"Term: {term}")
    if phase:
        print(f"Phase Filter: {phase}")
    print(f"{'='*80}\n")

    all_trials = []
    page_token = None
    page_count = 0
    total_count = 0

    # Paginate through all results
    while True:
        page_count += 1

        # Build search parameters
        search_params = {
            'intervention': term,
            'pageSize': 1000
        }

        # Add optional phase filter
        if phase:
            search_params['phase'] = phase

        # Add page token for pagination
        if page_token:
            search_params['pageToken'] = page_token

        # Search for trials
        result = search(**search_params)

        # Extract total count from first page only
        if page_count == 1:
            total_match = re.search(r'\*\*Results:\*\*\s+([\d,]+)\s+of\s+([\d,]+)\s+studies found', result)
            if total_match:
                total_count = int(total_match.group(2).replace(',', ''))
            else:
                # Fallback: count NCT IDs in response
                total_count = len(re.findall(r'###\s+\d+\.\s+NCT\d{8}', result))

        # Parse trials from this page
        trial_sections = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)[1:]  # Skip header
        nct_ids = re.findall(r'###\s+\d+\.\s+(NCT\d{8})', result)

        for nct_id, section in zip(nct_ids, trial_sections):
            trial = {'nct_id': nct_id}

            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|\*\*)', section)
            if title_match:
                trial['title'] = title_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|\*\*)', section)
            if status_match:
                trial['status'] = status_match.group(1).strip()

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|\*\*)', section)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()

            all_trials.append(trial)

        # Check for next page token
        # CT.gov API format: `pageToken: "TOKEN_STRING"`
        next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            page_token = next_token_match.group(1).strip()
            print(f"  Page {page_count} complete: {len(nct_ids)} trials. Fetching next page...")
        else:
            # No more pages
            print(f"  Page {page_count} complete: {len(nct_ids)} trials. No more pages.")
            break

    # Count statuses
    statuses = {}
    for trial in all_trials:
        status = trial.get('status', 'Unknown')
        statuses[status] = statuses.get(status, 0) + 1

    # Count phases
    phases = {}
    for trial in all_trials:
        phase_val = trial.get('phase', 'Not Applicable')
        phases[phase_val] = phases.get(phase_val, 0) + 1

    # Build summary
    summary = {
        'total_trials': total_count,
        'trials_retrieved': len(all_trials),
        'pages_fetched': page_count,
        'retrieval_note': f'Retrieved {len(all_trials)} of {total_count} total trials across {page_count} page(s)',
        'status_breakdown': dict(sorted(statuses.items(), key=lambda x: x[1], reverse=True)),
        'phase_breakdown': dict(sorted(phases.items(), key=lambda x: x[1], reverse=True))
    }

    return {
        'total_count': total_count,
        'trials_parsed': all_trials,
        'summary': summary
    }


# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Error: Search term required")
        print("\nUsage: python3 get_clinical_trials.py <TERM> [PHASE]")
        print("\nExamples:")
        print("  python3 get_clinical_trials.py 'GLP-1'")
        print("  python3 get_clinical_trials.py 'KRAS inhibitor'")
        print("  python3 get_clinical_trials.py 'heart failure' PHASE3")
        print("  python3 get_clinical_trials.py 'obesity' PHASE2")
        print("\nPhase options: PHASE1, PHASE2, PHASE3, PHASE4")
        sys.exit(1)

    term = sys.argv[1]
    phase = sys.argv[2] if len(sys.argv) > 2 else None

    result = get_clinical_trials(term, phase)

    print(f"\n{'='*80}")
    print(f"CLINICAL TRIALS ANALYSIS: {term}")
    if phase:
        print(f"Phase Filter: {phase}")
    print(f"{'='*80}\n")

    print(f"Total Trials in Database: {result['total_count']}")
    print(f"Trials Retrieved: {len(result['trials_parsed'])}")
    print(f"Pages Fetched: {result['summary']['pages_fetched']}")
    print(f"\nNote: {result['summary']['retrieval_note']}\n")

    summary = result['summary']

    # Display status breakdown
    if summary['status_breakdown']:
        print("Status Breakdown:")
        for status, count in summary['status_breakdown'].items():
            pct = (count / len(result['trials_parsed']) * 100) if result['trials_parsed'] else 0
            print(f"  {status}: {count} ({pct:.1f}%)")

    # Display phase breakdown
    if summary['phase_breakdown']:
        print("\nPhase Breakdown:")
        for phase_val, count in summary['phase_breakdown'].items():
            pct = (count / len(result['trials_parsed']) * 100) if result['trials_parsed'] else 0
            print(f"  {phase_val}: {count} ({pct:.1f}%)")

    print(f"\n{'='*80}")
