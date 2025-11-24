import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re

def get_heart_failure_phase3_trials():
    """Get Phase 3 heart failure clinical trials with endpoint extraction.

    Searches ClinicalTrials.gov for heart failure trials in Phase 3 across all statuses.
    Extracts primary endpoints for competitive analysis.

    Returns:
        dict: Contains total_count, trials data, and summary statistics
    """
    all_trials = []
    page_token = None
    page_count = 0

    print("Searching for Phase 3 heart failure trials...")

    # Search with comprehensive heart failure terms
    search_query = 'heart failure OR HF OR cardiac failure OR "congestive heart failure" OR CHF'

    while True:
        page_count += 1
        print(f"Fetching page {page_count}...")

        # Search with phase filter
        if page_token:
            result = search(
                query=search_query,
                filter_advanced='AREA[Phase]PHASE3',
                pageSize=1000,
                pageToken=page_token
            )
        else:
            result = search(
                query=search_query,
                filter_advanced='AREA[Phase]PHASE3',
                pageSize=1000
            )

        if not result:
            print("No results returned")
            break

        # Parse markdown response
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:  # Skip first empty split
            trial_data = {}

            # Extract NCT ID from the block
            nct_match = re.search(r'NCT\d{8}', block)
            if nct_match:
                trial_data['nct_id'] = nct_match.group()

            # Extract title
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if title_match:
                trial_data['title'] = title_match.group(1).strip()

            # Extract sponsor
            sponsor_match = re.search(r'\*\*Sponsor:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if sponsor_match:
                trial_data['sponsor'] = sponsor_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if status_match:
                trial_data['status'] = status_match.group(1).strip()

            # Extract enrollment
            enrollment_match = re.search(r'\*\*Enrollment:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if enrollment_match:
                trial_data['enrollment'] = enrollment_match.group(1).strip()

            # Extract study type
            study_type_match = re.search(r'\*\*Study Type:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if study_type_match:
                trial_data['study_type'] = study_type_match.group(1).strip()

            # Extract primary outcome (endpoint)
            outcome_match = re.search(r'\*\*Primary Outcome:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if outcome_match:
                trial_data['primary_endpoint'] = outcome_match.group(1).strip()

            # Extract interventions
            intervention_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if intervention_match:
                trial_data['interventions'] = intervention_match.group(1).strip()

            # Extract study design
            design_match = re.search(r'\*\*Study Design:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if design_match:
                trial_data['study_design'] = design_match.group(1).strip()

            if trial_data:
                all_trials.append(trial_data)

        # Check for next page
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match and next_token_match.group(1) != page_token:
            page_token = next_token_match.group(1)
            print(f"Found {len(all_trials)} trials so far, continuing...")
        else:
            break

    # Generate summary statistics
    status_counts = {}
    sponsor_counts = {}
    endpoint_categories = {
        'Mortality': 0,
        'Hospitalization': 0,
        'MACE': 0,
        'Exercise/Functional': 0,
        'Quality of Life': 0,
        'Composite': 0,
        'Other/Unknown': 0
    }

    for trial in all_trials:
        # Count statuses
        status = trial.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

        # Count sponsors
        sponsor = trial.get('sponsor', 'Unknown')
        sponsor_counts[sponsor] = sponsor_counts.get(sponsor, 0) + 1

        # Categorize endpoints
        endpoint = trial.get('primary_endpoint', '').lower()
        if 'death' in endpoint or 'mortality' in endpoint or 'survival' in endpoint:
            endpoint_categories['Mortality'] += 1
        elif 'hospitalization' in endpoint or 'admission' in endpoint:
            endpoint_categories['Hospitalization'] += 1
        elif 'mace' in endpoint or 'cardiovascular death' in endpoint:
            endpoint_categories['MACE'] += 1
        elif 'exercise' in endpoint or '6mw' in endpoint or 'functional' in endpoint or 'nyha' in endpoint:
            endpoint_categories['Exercise/Functional'] += 1
        elif 'quality of life' in endpoint or 'qol' in endpoint or 'kccq' in endpoint:
            endpoint_categories['Quality of Life'] += 1
        elif 'composite' in endpoint or ' and ' in endpoint:
            endpoint_categories['Composite'] += 1
        else:
            endpoint_categories['Other/Unknown'] += 1

    # Sort by frequency
    top_statuses = sorted(status_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_sponsors = sorted(sponsor_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    summary = {
        'total_trials': len(all_trials),
        'top_statuses': top_statuses,
        'top_sponsors': top_sponsors,
        'endpoint_categories': endpoint_categories,
        'pages_fetched': page_count
    }

    return {
        'total_count': len(all_trials),
        'data': all_trials,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_heart_failure_phase3_trials()

    print(f"\n{'='*80}")
    print(f"PHASE 3 HEART FAILURE CLINICAL TRIALS SUMMARY")
    print(f"{'='*80}\n")

    print(f"Total Phase 3 Heart Failure Trials: {result['total_count']}")
    print(f"Pages fetched: {result['summary']['pages_fetched']}\n")

    print("Top Trial Statuses:")
    for status, count in result['summary']['top_statuses']:
        print(f"  {status}: {count}")

    print("\nPrimary Endpoint Categories:")
    for category, count in result['summary']['endpoint_categories'].items():
        if count > 0:
            pct = (count / result['total_count'] * 100) if result['total_count'] > 0 else 0
            print(f"  {category}: {count} ({pct:.1f}%)")

    print("\nTop Sponsors:")
    for sponsor, count in result['summary']['top_sponsors'][:10]:
        print(f"  {sponsor}: {count}")

    print(f"\n{'='*80}")
    print(f"Data includes NCT IDs, titles, sponsors, endpoints, and study design")
    print(f"{'='*80}\n")
