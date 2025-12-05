import sys
sys.path.insert(0, ".claude")
from datetime import datetime
from mcp.servers.fda_mcp import lookup_drug

def get_glp1_fda_drugs():
    """Get FDA approved GLP-1 receptor agonist drugs.

    Searches for all major GLP-1 drugs: semaglutide, tirzepatide, liraglutide,
    dulaglutide, exenatide, albiglutide, lixisenatide.

    Returns:
        dict: Contains 'drugs' (list of drug dicts) and 'summary' (formatted string)
    """
    # GLP-1 active ingredients to search
    glp1_drugs = [
        "semaglutide",
        "tirzepatide",
        "liraglutide",
        "dulaglutide",
        "exenatide",
        "albiglutide",
        "lixisenatide"
    ]

    all_drugs = []

    for drug_name in glp1_drugs:
        try:
            # Use count-first pattern (MANDATORY for FDA) to avoid token overflow
            result = lookup_drug(
                search_term=drug_name,
                search_type="general",
                count="openfda.brand_name.exact",
                limit=100
            )

            # Handle response format (nested under 'data')
            data = result.get('data', {})
            if not data:
                continue

            # For count query, results are brand names with counts
            # We need a second query to get full details
            detail_result = lookup_drug(
                search_term=drug_name,
                search_type="general",
                limit=10
            )

            detail_data = detail_result.get('data', {})
            results_list = detail_data.get('results', [])

            for drug in results_list:
                # Extract key fields safely
                drug_info = {
                    'active_ingredient': drug.get('openfda', {}).get('generic_name', ['Unknown'])[0] if drug.get('openfda', {}).get('generic_name') else drug_name,
                    'brand_name': drug.get('openfda', {}).get('brand_name', ['Unknown'])[0] if drug.get('openfda', {}).get('brand_name') else 'Unknown',
                    'manufacturer': drug.get('openfda', {}).get('manufacturer_name', ['Unknown'])[0] if drug.get('openfda', {}).get('manufacturer_name') else 'Unknown',
                    'approval_date': drug.get('approval_date', 'Unknown'),
                    'dosage_form': drug.get('dosage_form', 'Unknown'),
                    'route': drug.get('route', 'Unknown'),
                    'application_number': drug.get('application_number', 'Unknown'),
                    'indications': drug.get('indications_and_usage', ['Not specified'])[0][:200] + '...' if drug.get('indications_and_usage') and drug.get('indications_and_usage')[0] else 'Not specified'
                }
                all_drugs.append(drug_info)

        except Exception as e:
            print(f"Error searching for {drug_name}: {str(e)}")
            continue

    # Remove duplicates based on application_number
    seen = set()
    unique_drugs = []
    for drug in all_drugs:
        app_num = drug['application_number']
        if app_num not in seen:
            seen.add(app_num)
            unique_drugs.append(drug)

    # Sort by approval_date (most recent first)
    unique_drugs.sort(key=lambda x: x['approval_date'], reverse=True)

    # Create summary
    summary_lines = [f"\n=== FDA Approved GLP-1 Receptor Agonists ==="]
    summary_lines.append(f"Total unique drugs found: {len(unique_drugs)}\n")

    for drug in unique_drugs:
        summary_lines.append(f"Drug: {drug['brand_name']}")
        summary_lines.append(f"  Active Ingredient: {drug['active_ingredient']}")
        summary_lines.append(f"  Manufacturer: {drug['manufacturer']}")
        summary_lines.append(f"  Approval Date: {drug['approval_date']}")
        summary_lines.append(f"  Dosage Form: {drug['dosage_form']}")
        summary_lines.append(f"  Route: {drug['route']}")
        summary_lines.append(f"  Application: {drug['application_number']}")
        summary_lines.append(f"  Indications: {drug['indications']}")
        summary_lines.append("")

    summary = "\n".join(summary_lines)

    return {
        'data': {
            'drugs': unique_drugs,
            'total_count': len(unique_drugs)
        },
        'source_metadata': {
            'source': 'FDA Drug Database',
            'mcp_server': 'fda_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {
                'search_terms': glp1_drugs,
                'search_type': 'general',
                'limit': 100
            },
            'data_count': len(unique_drugs),
            'data_type': 'fda_approved_drugs'
        },
        'summary': f"{summary}\n(source: FDA Drug Database, {datetime.now().strftime('%Y-%m-%d')})"
    }

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    import json
    result = get_glp1_fda_drugs()

    # For human-readable output (comment out for JSON verification)
    # print(result['summary'])
    # print(f"\nReturned {result['data']['total_count']} unique GLP-1 drugs")

    # For JSON verification (required by verify_source_attribution.py)
    print(json.dumps(result, indent=2))
