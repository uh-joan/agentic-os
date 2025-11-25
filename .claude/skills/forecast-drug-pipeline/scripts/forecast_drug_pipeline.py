import sys
import re
from datetime import datetime
from collections import defaultdict
from math import ceil
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search, get_study


def parse_trial_detail(nct_id, trial_detail):
    """Parse detailed trial information from get_study() markdown response."""

    def extract_field(pattern, text, default="Not specified"):
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else default

    # Extract completion date (use Study Completion, not Primary Completion Date)
    completion_date = extract_field(r'\*\*Study Completion:\*\*\s*(.+?)(?=\n|$)', trial_detail)

    # Extract other key fields
    title = extract_field(r'\*\*Study Title:\*\*\s*(.+?)(?=\n|$)', trial_detail)
    status = extract_field(r'\*\*Status:\*\*\s*(.+?)(?=\n|$)', trial_detail)
    phase = extract_field(r'\*\*Phase:\*\*\s*(.+?)(?=\n|$)', trial_detail)
    sponsor = extract_field(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?=\(|$)', trial_detail)

    # Conditions section
    condition_match = re.search(r'## Conditions\s+[-\s]+(.*?)(?=\n##|\Z)', trial_detail, re.DOTALL)
    condition = condition_match.group(1).strip() if condition_match else "Not specified"

    # Interventions section
    intervention_match = re.search(r'## Interventions\s+###\s+([^:]+):\s+(.+?)(?=\n##|\Z)', trial_detail, re.DOTALL)
    if intervention_match:
        intervention_type = intervention_match.group(1).strip()
        intervention = intervention_match.group(2).strip().split('\n')[0]  # First line
    else:
        intervention_type = "Not specified"
        intervention = "Not specified"

    enrollment = extract_field(r'\*\*Enrollment:\*\*\s*(\d+)', trial_detail, "0")

    return {
        'nct_id': nct_id,
        'title': title,
        'status': status,
        'phase': phase,
        'completion_date': completion_date,
        'sponsor': sponsor,
        'condition': condition,
        'intervention': intervention,
        'intervention_type': intervention_type,
        'enrollment': int(enrollment) if enrollment.isdigit() else 0
    }


def build_search_term(search_criteria):
    """Build CT.gov search term from criteria dict.

    Args:
        search_criteria: Dict with keys:
            - route: Administration route (e.g., "subcutaneous", "oral", "intravenous")
            - therapeutic_area: Disease/condition (e.g., "diabetes", "cancer")
            - sponsor: Company name (e.g., "Pfizer", "Moderna")
            - intervention_type: Type (e.g., "biological", "drug")

    Returns:
        str: Combined search term for CT.gov
    """
    terms = []

    if 'route' in search_criteria:
        terms.append(search_criteria['route'])

    if 'therapeutic_area' in search_criteria:
        terms.append(search_criteria['therapeutic_area'])

    if 'intervention_type' in search_criteria:
        terms.append(search_criteria['intervention_type'])

    # Sponsor handled separately (CT.gov has sponsor parameter)
    return ' '.join(terms) if terms else None


def forecast_drug_pipeline(
    search_criteria,
    completion_years=None,
    phase="PHASE3",
    approval_offset_years=2
):
    """Forecast drug pipeline with flexible search criteria.

    Args:
        search_criteria: Dict with keys like:
            - route: Administration route (e.g., "subcutaneous", "oral", "intravenous", "inhalation")
            - therapeutic_area: Disease/condition (e.g., "diabetes", "cancer", "Alzheimer")
            - sponsor: Company name (e.g., "Pfizer", "Moderna", "Eli Lilly")
            - intervention_type: Drug, biological, device
        completion_years: List of years for trial completion (default: [2024, 2025])
        phase: Clinical trial phase (default: "PHASE3")
        approval_offset_years: Years after completion to forecast approval (default: 2)

    Returns:
        dict: Contains total_count, target_count, trials, summary, and forecast

    Examples:
        # Subcutaneous drugs for 2026-2027 approval
        forecast_drug_pipeline({"route": "subcutaneous"}, [2024, 2025])

        # Oral diabetes drugs for 2027-2028 approval
        forecast_drug_pipeline(
            {"route": "oral", "therapeutic_area": "diabetes"},
            [2025, 2026]
        )

        # Pfizer biologics for 2026-2027 approval
        forecast_drug_pipeline(
            {"sponsor": "Pfizer", "intervention_type": "biological"},
            [2024, 2025]
        )
    """

    if completion_years is None:
        completion_years = [2024, 2025]

    # Calculate forecast approval years
    forecast_years = [year + approval_offset_years for year in completion_years]
    forecast_start = min(forecast_years)
    forecast_end = max(forecast_years)

    print(f"Forecasting drug pipeline approval for {forecast_start}-{forecast_end}...")
    print(f"Search Criteria: {search_criteria}")
    print(f"Completion Years: {completion_years}")
    print(f"Phase: {phase}")
    print()

    # Build search parameters
    search_term = build_search_term(search_criteria)
    sponsor = search_criteria.get('sponsor')

    print("Step 1: Searching clinical trials...")

    # Step 1a: Quick query to get total count
    search_params = {"phase": phase, "pageSize": 1}
    if search_term:
        search_params["term"] = search_term
    if sponsor:
        search_params["lead"] = sponsor

    result_preview = search(**search_params)

    # Extract total available (handle comma-separated numbers like "3,028")
    total_match = re.search(r'\*\*Results:\*\*\s*[\d,]+\s*of\s*([\d,]+)', result_preview)
    if not total_match:
        print("Could not determine total trial count")
        return {
            'total_count': 0,
            'target_count': 0,
            'trials': [],
            'summary': {},
            'forecast': {
                'years': f"{forecast_start}-{forecast_end}",
                'completion_years': completion_years,
                'approval_offset': approval_offset_years
            }
        }

    total_available = int(total_match.group(1).replace(',', ''))
    print(f"  Found {total_available} total trials available")

    # Step 1b: Calculate optimal pageSize to fetch all trials in 2 pages
    optimal_page_size = ceil(total_available / 2)
    print(f"  Using optimal pageSize={optimal_page_size} (fetches all trials in 2 pages)")

    # Step 1c: Collect NCT IDs from all pages (using set for deduplication)
    all_nct_ids = set()
    page_num = 1
    next_token = None

    search_params["pageSize"] = optimal_page_size

    while True:
        if next_token:
            search_params["pageToken"] = next_token

        result = search(**search_params)

        if not result:
            break

        # Extract NCT IDs (set automatically deduplicates)
        page_nct_ids = set(re.findall(r'NCT\d{8}', result))
        all_nct_ids.update(page_nct_ids)

        print(f"  Page {page_num}: collected {len(page_nct_ids)} trials (total: {len(all_nct_ids)})")

        # Check for next page token
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            next_token = next_token_match.group(1)
            page_num += 1
        else:
            print(f"  Completed: {page_num} page(s), {len(all_nct_ids)} unique trials")
            break

    nct_ids = list(all_nct_ids)
    total_count = len(nct_ids)

    print(f"\nStep 2: Fetching detailed information for all {total_count} trials...")
    print(f"  (This may take several minutes for {total_count} trials)")

    # Step 2: Fetch detailed trial data for each NCT ID
    all_trials = []
    error_count = 0

    for i, nct_id in enumerate(nct_ids, 1):
        # Progress indicator every 100 trials
        if i % 100 == 0 or i == total_count:
            print(f"  Progress: {i}/{total_count} ({len(all_trials)} successful, {error_count} errors)")

        try:
            # Get full trial details
            trial_detail = get_study(nctId=nct_id)

            if not trial_detail:
                error_count += 1
                continue

            # Parse detailed information
            trial_data = parse_trial_detail(nct_id, trial_detail)
            if trial_data:
                all_trials.append(trial_data)
            else:
                error_count += 1

        except Exception as e:
            error_count += 1
            if error_count <= 3:  # Show first 3 errors
                print(f"    Error on {nct_id}: {str(e)[:60]}")
            continue

    print(f"\nCompleted: {len(all_trials)} trials retrieved ({error_count} errors)")

    print(f"\nStep 3: Filtering for trials likely to lead to {forecast_start}-{forecast_end} approval...")

    # Step 3: Filter for completion_years
    target_trials = []

    for trial in all_trials:
        completion_date = trial.get('completion_date', '')

        if not completion_date or completion_date == "Not specified":
            continue

        # Strip "(Estimated)" or "(Actual)" suffix
        completion_date = re.sub(r'\s*\((Estimated|Actual)\)\s*$', '', completion_date).strip()

        # Try to parse the date robustly (multiple formats)
        parsed_date = None
        for fmt in ['%B %d, %Y', '%B %Y', '%Y-%m-%d', '%m/%Y', '%Y']:
            try:
                parsed_date = datetime.strptime(completion_date, fmt)
                break
            except:
                continue

        if parsed_date:
            year = parsed_date.year

            # Include trials completing in specified years
            if year in completion_years:
                target_trials.append(trial)

    print(f"  Found {len(target_trials)} trials completing in {completion_years}")

    # Analyze therapeutic areas
    therapeutic_areas = {}
    sponsors = {}
    status_counts = {}

    for trial in target_trials:
        # Count therapeutic areas
        condition = trial.get('condition', 'Unknown')
        therapeutic_areas[condition] = therapeutic_areas.get(condition, 0) + 1

        # Count sponsors
        sponsor = trial.get('sponsor', 'Unknown')
        sponsors[sponsor] = sponsors.get(sponsor, 0) + 1

        # Count statuses
        status = trial.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    # Sort by frequency
    top_areas = sorted(therapeutic_areas.items(), key=lambda x: x[1], reverse=True)[:10]
    top_sponsors = sorted(sponsors.items(), key=lambda x: x[1], reverse=True)[:10]

    # Create summary
    summary = {
        'total_trials': len(all_trials),
        'likely_approval': len(target_trials),
        'top_therapeutic_areas': top_areas,
        'top_sponsors': top_sponsors,
        'status_distribution': status_counts,
        'completion_years_breakdown': {
            str(year): sum(1 for t in target_trials if str(year) in t.get('completion_date', ''))
            for year in completion_years
        }
    }

    return {
        'total_count': len(all_trials),
        'target_count': len(target_trials),
        'trials': target_trials,
        'summary': summary,
        'forecast': {
            'years': f"{forecast_start}-{forecast_end}",
            'completion_years': completion_years,
            'approval_offset': approval_offset_years,
            'search_criteria': search_criteria
        }
    }


if __name__ == "__main__":
    import json

    # Example 1: Subcutaneous drugs for 2026-2027 approval
    print("="*80)
    print("EXAMPLE 1: Subcutaneous Drugs Pipeline (2026-2027 Approval)")
    print("="*80)
    print()

    result = forecast_drug_pipeline(
        search_criteria={"route": "subcutaneous"},
        completion_years=[2024, 2025],
        phase="PHASE3",
        approval_offset_years=2
    )

    print("\n" + "="*80)
    print(f"DRUG PIPELINE FORECAST: {result['forecast']['years']} APPROVAL")
    print("="*80)

    print(f"\nSearch Criteria: {result['forecast']['search_criteria']}")
    print(f"Total {result['forecast']['search_criteria'].get('route', 'Phase 3')} trials: {result['total_count']}")
    print(f"Trials likely for {result['forecast']['years']} approval: {result['target_count']}")

    summary = result['summary']

    print(f"\nCompletion Timeline:")
    for year, count in summary['completion_years_breakdown'].items():
        print(f"  • Completing in {year}: {count} trials")

    print(f"\nTrial Status Distribution:")
    for status, count in sorted(summary['status_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {status}: {count} trials")

    print(f"\nTop Therapeutic Areas:")
    for i, (area, count) in enumerate(summary['top_therapeutic_areas'], 1):
        print(f"  {i}. {area}: {count} trials")

    print(f"\nTop Sponsors:")
    for i, (sponsor, count) in enumerate(summary['top_sponsors'], 1):
        print(f"  {i}. {sponsor}: {count} trials")

    print(f"\n" + "="*80)
    print("FORECAST METHODOLOGY")
    print("="*80)
    print(f"\nApproval Timeline Rationale:")
    print(f"• Phase 3 trials completing in {result['forecast']['completion_years']}")
    print(f"• Typical FDA review: {result['forecast']['approval_offset']} years")
    print(f"• Expected approval window: {result['forecast']['years']}")
    print("\nNote: This is a probabilistic forecast based on completion dates.")
    print("Actual approval depends on trial results, FDA review speed, and regulatory factors.")
