import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_obesity_fda_drugs():
    """Get FDA-approved obesity drugs in the US.

    Uses the adverse events database drugindication field to discover drugs
    prescribed for obesity-related conditions. Filters results to focus on
    drugs primarily prescribed for obesity (not incidentally mentioned).

    Returns:
        dict: Contains drugs list, total count, and formatted summary
    """
    # Search obesity-related indications in adverse events database
    indication_terms = [
        "obesity",
        "weight control",
        "overweight"
    ]

    all_drugs = {}  # Deduplication by brand_name

    for indication in indication_terms:
        try:
            # Query adverse events database for this indication
            result = lookup_drug(
                search_term=f"patient.drug.drugindication:{indication}",
                search_type="adverse_events",
                count="patient.drug.openfda.brand_name.exact",
                limit=100
            )

            if not result or 'data' not in result:
                continue

            data = result.get('data', {})
            brand_results = data.get('results', [])

            print(f"Indication '{indication}': Found {len(brand_results)} brands")

            for brand_item in brand_results:
                brand_name = brand_item.get('term')
                adverse_event_count = brand_item.get('count', 0)

                if brand_name:
                    if brand_name not in all_drugs:
                        all_drugs[brand_name] = {
                            'brand_name': brand_name,
                            'indications': {},
                            'total_adverse_events': 0,
                            'obesity_events': 0  # Track primary obesity indication
                        }

                    # Track which indications this drug appears under
                    all_drugs[brand_name]['indications'][indication] = adverse_event_count
                    all_drugs[brand_name]['total_adverse_events'] += adverse_event_count

                    # Track primary obesity indication separately
                    if indication == "obesity":
                        all_drugs[brand_name]['obesity_events'] = adverse_event_count

        except Exception as e:
            print(f"Error searching indication '{indication}': {str(e)}")
            continue

    # Filter to drugs with significant obesity indication
    # Rule: Must have obesity-specific events OR high obesity-to-total ratio
    filtered_drugs = []
    for drug in all_drugs.values():
        obesity_count = drug.get('obesity_events', 0)
        total_count = drug.get('total_adverse_events', 0)

        # Include if:
        # 1. Has >= 400 obesity-specific adverse events, OR
        # 2. Obesity events are >= 25% of total (indicates primary obesity use)
        obesity_ratio = obesity_count / total_count if total_count > 0 else 0

        if obesity_count >= 400 or obesity_ratio >= 0.25:
            filtered_drugs.append(drug)

    # Sort by obesity event count (most relevant first)
    sorted_drugs = sorted(
        filtered_drugs,
        key=lambda x: x['obesity_events'],
        reverse=True
    )

    # Generate summary
    summary = []
    summary.append("FDA-Approved Obesity Drugs in the US\n")
    summary.append(f"Total drugs found: {len(sorted_drugs)}\n")
    summary.append("(Filtered to drugs with significant obesity indication)\n")
    summary.append("\nDrugs by Obesity-Specific Usage:")
    summary.append("━" * 60)

    for idx, drug in enumerate(sorted_drugs, 1):
        indications_str = ", ".join([
            f"{ind}({count:,})"
            for ind, count in drug['indications'].items()
        ])

        summary.append(f"\n{idx}. {drug['brand_name']}")
        summary.append(f"   Obesity-Specific Reports: {drug['obesity_events']:,}")
        summary.append(f"   Total Reports: {drug['total_adverse_events']:,}")
        summary.append(f"   All Indications: {indications_str}")

    summary.append("\n\n" + "━" * 60)
    summary.append("DATA SOURCE: FDA Adverse Events Database")
    summary.append("METHOD: Search patient.drug.drugindication field for obesity-related terms")
    summary.append("\nFILTERING: Only drugs with >=400 obesity-specific reports")
    summary.append("or >=25% obesity ratio (filters out incidental mentions)")
    summary.append("\nNOTE: Adverse event counts reflect real-world usage,")
    summary.append("not approval status. Sorted by obesity-specific reports.")

    return {
        'drugs': sorted_drugs,
        'total_count': len(sorted_drugs),
        'summary': '\n'.join(summary)
    }

if __name__ == "__main__":
    result = get_obesity_fda_drugs()
    print(result['summary'])
