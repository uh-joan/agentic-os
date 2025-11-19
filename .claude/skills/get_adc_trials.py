import sys
import re
sys.path.insert(0, "scripts")
from mcp.servers.ct_gov_mcp import search

def get_adc_trials():
    """Get antibody-drug conjugate (ADC) clinical trials across all phases.

    Uses pagination to retrieve complete dataset from ClinicalTrials.gov.
    Handles potential >1000 trial results by making multiple requests.

    Returns:
        dict: Contains total_count, trials_parsed, and summary
    """

    all_trials = []
    page_token = None
    page_count = 0
    total_count = 0

    # Paginate through all results
    while True:
        page_count += 1

        # Search for ADC related trials with pagination
        result = search(
            intervention="antibody-drug conjugate",
            pageSize=1000,
            pageToken=page_token
        )

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

    # Count statuses and phases
    statuses = {}
    phases = {}
    for trial in all_trials:
        status = trial.get('status', 'Unknown')
        statuses[status] = statuses.get(status, 0) + 1

        phase = trial.get('phase', 'Unknown')
        phases[phase] = phases.get(phase, 0) + 1

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
    result = get_adc_trials()

    print(f"\n{'='*80}")
    print(f"ADC CLINICAL TRIALS ANALYSIS")
    print(f"{'='*80}\n")

    print(f"Total Trials in Database: {result['total_count']}")
    print(f"Trials Retrieved: {len(result['trials_parsed'])}")
    print(f"Note: {result['summary']['retrieval_note']}\n")

    summary = result['summary']

    print("PHASE BREAKDOWN:")
    print("-" * 40)
    for phase, count in summary['phase_breakdown'].items():
        print(f"  {phase:30s}: {count:4d}")

    print("\nSTATUS BREAKDOWN:")
    print("-" * 40)
    for status, count in summary['status_breakdown'].items():
        print(f"  {status:30s}: {count:4d}")

    print(f"\n{'='*80}\n")
