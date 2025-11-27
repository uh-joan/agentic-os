import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug
from collections import defaultdict
from datetime import datetime

# Get current year for default end_year
CURRENT_YEAR = datetime.now().year

def get_fda_approvals_timeline_by_indication(
    therapeutic_area: str,
    drugs: list,
    start_year: int = 2015,
    end_year: int = None
):
    """Get FDA drug approvals with timeline analysis by therapeutic area.

    Args:
        therapeutic_area: Display name for the therapeutic area (e.g., "Diabetes", "GLP-1 Agonists")
        drugs: List of drug names to search (e.g., ["semaglutide", "metformin", "insulin glargine"])
        start_year: Start of analysis period (default: 2015)
        end_year: End of analysis period (default: current year)

    Returns:
        dict: {
            'therapeutic_area': str,
            'total_approvals': int,
            'approvals_by_year': dict,
            'drugs_by_year': dict,
            'average_per_year': float,
            'trend': str,
            'summary': str
        }
    """

    # Set end_year to current year if not specified
    if end_year is None:
        end_year = CURRENT_YEAR

    # Validate inputs
    if not drugs or not isinstance(drugs, list):
        raise ValueError("drugs parameter is required and must be a non-empty list of drug names")

    print(f"\n{'='*70}")
    print(f"FDA Approvals Timeline Analysis: {therapeutic_area}")
    print(f"Period: {start_year}-{end_year}")
    print(f"Searching {len(drugs)} drugs...")
    print(f"{'='*70}\n")

    all_approvals = []
    approvals_by_year = defaultdict(int)
    drugs_by_year = defaultdict(list)

    # Search each drug using proven FDA pattern
    for drug_name in drugs:
        print(f"Searching: {drug_name}...")

        try:
            # Step 1: Count query to get brand names (MANDATORY for FDA)
            count_result = lookup_drug(
                search_term=drug_name,
                search_type="general",
                count="openfda.brand_name.exact",
                limit=50
            )

            data = count_result.get('data', {})
            brand_results = data.get('results', [])

            if not brand_results:
                print(f"  ✗ No brands found")
                continue

            print(f"  ✓ Found {len(brand_results)} brand(s)")

            # Step 2: Get detail for this drug (limited query to avoid token overflow)
            detail_result = lookup_drug(
                search_term=drug_name,
                search_type="general",
                limit=20  # Reasonable limit to get approvals without token overflow
            )

            detail_data = detail_result.get('data', {})
            results_list = detail_data.get('results', [])

            for drug in results_list:
                # Safely extract fields
                openfda = drug.get('openfda', {})
                submissions = drug.get('submissions', [])

                # Find the original approval submission
                # Look for ORIG (original) submissions with AP (approved) status
                approval_date_str = ''
                for submission in submissions:
                    sub_type = submission.get('submission_type', '')
                    sub_status = submission.get('submission_status', '')
                    sub_date = submission.get('submission_status_date', '')

                    # Original approval submission
                    if sub_type == 'ORIG' and sub_status == 'AP' and sub_date:
                        approval_date_str = sub_date
                        break

                # Fallback: if no ORIG found, use earliest approved submission
                if not approval_date_str:
                    approved_submissions = [s for s in submissions
                                          if s.get('submission_status') == 'AP'
                                          and s.get('submission_status_date')]
                    if approved_submissions:
                        # Sort by date and take earliest
                        approved_submissions.sort(key=lambda x: x.get('submission_status_date', ''))
                        approval_date_str = approved_submissions[0].get('submission_status_date', '')

                if not approval_date_str:
                    continue

                # Parse year from approval date (handle YYYYMMDD or YYYY-MM-DD formats)
                try:
                    if len(approval_date_str) >= 4:
                        if '-' in approval_date_str:
                            approval_year = int(approval_date_str.split('-')[0])
                        else:
                            approval_year = int(approval_date_str[:4])
                    else:
                        continue

                    # Filter by year range
                    if approval_year < start_year or approval_year > end_year:
                        continue

                except (ValueError, IndexError):
                    continue

                # Extract drug info
                drug_info = {
                    'brand_name': openfda.get('brand_name', ['Unknown'])[0] if openfda.get('brand_name') else 'Unknown',
                    'generic_name': openfda.get('generic_name', [drug_name])[0] if openfda.get('generic_name') else drug_name,
                    'manufacturer': openfda.get('manufacturer_name', ['Unknown'])[0] if openfda.get('manufacturer_name') else 'Unknown',
                    'approval_date': approval_date_str,
                    'approval_year': approval_year,
                    'application_number': openfda.get('application_number', ['Unknown'])[0] if openfda.get('application_number') else 'Unknown'
                }

                all_approvals.append(drug_info)
                approvals_by_year[approval_year] += 1
                drugs_by_year[approval_year].append(drug_info)

        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
            continue

    # Calculate statistics
    total_approvals = len(all_approvals)
    years_in_range = end_year - start_year + 1
    average_per_year = total_approvals / years_in_range if years_in_range > 0 else 0.0

    # Determine trend
    trend = "no_data"
    if len(approvals_by_year) >= 2:
        years_sorted = sorted(approvals_by_year.keys())
        mid_point = len(years_sorted) // 2
        first_half_avg = sum(approvals_by_year[y] for y in years_sorted[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(approvals_by_year[y] for y in years_sorted[mid_point:]) / (len(years_sorted) - mid_point)

        if second_half_avg > first_half_avg * 1.2:
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"

    # Create visualization (ASCII bar chart)
    visualization_lines = []
    if total_approvals > 0:
        # Find max count for scaling
        all_years = list(range(start_year, end_year + 1))
        max_count = max(approvals_by_year.values()) if approvals_by_year else 1
        max_bar_width = 50

        visualization_lines.append("\nTimeline Visualization:")
        visualization_lines.append(f"{'Year':<6} {'Count':<6} {'Bar'}")
        visualization_lines.append("-" * 70)

        for year in all_years:
            count = approvals_by_year.get(year, 0)
            # Scale bar width
            bar_width = int((count / max_count) * max_bar_width) if max_count > 0 else 0
            bar = '█' * bar_width
            visualization_lines.append(f"{year}   {count:<6} {bar}")

        visualization_lines.append("")

    # Create summary
    summary_lines = [
        f"\n{'='*70}",
        f"FDA Approvals Timeline: {therapeutic_area} ({start_year}-{end_year})",
        f"{'='*70}",
        f"\nTotal Approvals: {total_approvals}",
        f"Average per Year: {average_per_year:.1f}",
        f"Trend: {trend.upper()}"
    ]

    # Add visualization
    summary_lines.extend(visualization_lines)

    # Show complete timeline (all years, including zeros)
    summary_lines.append("Complete Timeline:")
    all_years = list(range(start_year, end_year + 1))
    for year in all_years:
        count = approvals_by_year.get(year, 0)
        if count > 0:
            drugs_in_year = drugs_by_year[year]
            summary_lines.append(f"  {year}: {count} approval{'s' if count != 1 else ''}")
            for drug in drugs_in_year[:3]:  # Show first 3 per year
                summary_lines.append(f"    • {drug['brand_name']} ({drug['generic_name']})")
            if len(drugs_in_year) > 3:
                summary_lines.append(f"    ... and {len(drugs_in_year) - 3} more")
        else:
            summary_lines.append(f"  {year}: 0 approvals")
    summary_lines.append("")

    summary = "\n".join(summary_lines)

    return {
        'therapeutic_area': therapeutic_area,
        'total_approvals': total_approvals,
        'approvals_by_year': dict(approvals_by_year),
        'drugs_by_year': {year: drugs for year, drugs in drugs_by_year.items()},
        'average_per_year': round(average_per_year, 1),
        'trend': trend,
        'summary': summary,
        'all_approvals': all_approvals
    }

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    # Test with GLP-1 drugs
    print("\n" + "="*70)
    print("Testing FDA Approvals Timeline Skill")
    print("="*70)

    # Test 1: GLP-1 drugs
    glp1_drugs = ["semaglutide", "tirzepatide", "liraglutide", "dulaglutide", "exenatide", "lixisenatide"]
    result = get_fda_approvals_timeline_by_indication(
        therapeutic_area="GLP-1 Agonists",
        drugs=glp1_drugs,
        start_year=2020  # Last 5 years
    )

    print(result['summary'])
    print(f"\n✓ Returned {result['total_approvals']} approvals")
    print(f"✓ Trend: {result['trend']}")
    print(f"✓ Analysis period: 2020-{CURRENT_YEAR}")

    # Test 2: PCSK9 inhibitors
    print("\n" + "="*70)
    print("Testing with PCSK9 Inhibitors (2015-2023)")
    print("="*70)

    pcsk9_drugs = ["evolocumab", "alirocumab", "inclisiran"]
    result2 = get_fda_approvals_timeline_by_indication(
        therapeutic_area="PCSK9 Inhibitors",
        drugs=pcsk9_drugs,
        start_year=2015,
        end_year=2023  # Explicit end year
    )

    print(result2['summary'])
    print(f"\n✓ Returned {result2['total_approvals']} approvals")
    print(f"✓ Trend: {result2['trend']}")
    print(f"\n{'='*70}\n")
