import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_alzheimers_fda_drugs():
    """Get FDA approved Alzheimer's disease drugs.

    Searches for all major Alzheimer's drugs across different mechanism classes:
    - Cholinesterase inhibitors
    - NMDA receptor antagonists
    - Anti-amyloid antibodies
    - Combination therapies

    Returns:
        dict: Contains 'drugs' (list of drug dicts), 'total_count',
              'drugs_by_class', and 'summary' (formatted string)
    """
    # Alzheimer's drugs to search by active ingredient
    alzheimers_drugs = {
        "Cholinesterase inhibitors": [
            "donepezil",
            "rivastigmine",
            "galantamine",
            "tacrine"  # discontinued but historically approved
        ],
        "NMDA receptor antagonists": [
            "memantine"
        ],
        "Anti-amyloid antibodies": [
            "aducanumab",
            "lecanemab",
            "donanemab"
        ],
        "Combination therapies": [
            "donepezil and memantine"
        ]
    }

    all_drugs = []
    drugs_by_class = {}

    for drug_class, drug_names in alzheimers_drugs.items():
        class_drugs = []

        for drug_name in drug_names:
            try:
                # Get drug details from FDA
                result = lookup_drug(
                    search_term=drug_name,
                    search_type="general",
                    limit=25
                )

                # Handle response format
                data = result.get('data', {})
                if not data:
                    continue

                results_list = data.get('results', [])

                for drug in results_list:
                    # Extract key fields safely
                    drug_info = {
                        'drug_class': drug_class,
                        'active_ingredient': drug.get('openfda', {}).get('generic_name', ['Unknown'])[0] if drug.get('openfda', {}).get('generic_name') else drug_name,
                        'brand_name': drug.get('openfda', {}).get('brand_name', ['Unknown'])[0] if drug.get('openfda', {}).get('brand_name') else 'Unknown',
                        'manufacturer': drug.get('openfda', {}).get('manufacturer_name', ['Unknown'])[0] if drug.get('openfda', {}).get('manufacturer_name') else 'Unknown',
                        'approval_date': drug.get('approval_date', 'Unknown'),
                        'dosage_form': drug.get('dosage_form', 'Unknown'),
                        'route': drug.get('route', 'Unknown'),
                        'application_number': drug.get('application_number', 'Unknown'),
                        'indications': drug.get('indications_and_usage', ['Not specified'])[0][:300] + '...' if drug.get('indications_and_usage') and len(drug.get('indications_and_usage')[0]) > 300 else (drug.get('indications_and_usage', ['Not specified'])[0] if drug.get('indications_and_usage') else 'Not specified')
                    }
                    all_drugs.append(drug_info)
                    class_drugs.append(drug_info)

            except Exception as e:
                print(f"Error searching for {drug_name}: {str(e)}")
                continue

        drugs_by_class[drug_class] = len(class_drugs)

    # Remove duplicates based on application_number
    seen = set()
    unique_drugs = []
    for drug in all_drugs:
        app_num = drug['application_number']
        if app_num not in seen and app_num != 'Unknown':
            seen.add(app_num)
            unique_drugs.append(drug)

    # Sort by approval_date (most recent first)
    unique_drugs.sort(key=lambda x: x['approval_date'], reverse=True)

    # Create summary
    summary_lines = ["\n=== FDA Approved Alzheimer's Disease Drugs ==="]
    summary_lines.append(f"Total unique drugs found: {len(unique_drugs)}\n")

    summary_lines.append("DRUGS BY CLASS:")
    for drug_class, count in drugs_by_class.items():
        summary_lines.append(f"  {drug_class}: {count}")

    summary_lines.append("\nDETAILED DRUG INFORMATION:\n")

    current_class = None
    for drug in unique_drugs:
        if drug['drug_class'] != current_class:
            current_class = drug['drug_class']
            summary_lines.append(f"\n--- {current_class} ---")

        summary_lines.append(f"\nDrug: {drug['brand_name']}")
        summary_lines.append(f"  Active Ingredient: {drug['active_ingredient']}")
        summary_lines.append(f"  Manufacturer: {drug['manufacturer']}")
        summary_lines.append(f"  Approval Date: {drug['approval_date']}")
        summary_lines.append(f"  Dosage Form: {drug['dosage_form']}")
        summary_lines.append(f"  Route: {drug['route']}")
        summary_lines.append(f"  Application: {drug['application_number']}")
        if len(drug['indications']) < 200:
            summary_lines.append(f"  Indications: {drug['indications']}")

    summary = "\n".join(summary_lines)

    return {
        'drugs': unique_drugs,
        'total_count': len(unique_drugs),
        'drugs_by_class': drugs_by_class,
        'summary': summary
    }

# REQUIRED: Make skill executable standalone
if __name__ == "__main__":
    result = get_alzheimers_fda_drugs()
    print(result['summary'])
    print(f"\nReturned {result['total_count']} unique Alzheimer's drugs")
