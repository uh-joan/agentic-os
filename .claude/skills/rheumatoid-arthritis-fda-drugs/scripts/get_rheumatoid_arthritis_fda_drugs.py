import sys
sys.path.insert(0, "scripts")
from mcp.servers.fda_mcp import lookup_drug
import re
from datetime import datetime

def get_rheumatoid_arthritis_fda_drugs():
    """Get FDA-approved drugs for rheumatoid arthritis.

    Returns:
        dict: Contains total_count and drugs_summary with drug details
    """
    result = lookup_drug(
        search_term="rheumatoid arthritis",
        search_type="label",
        limit=100
    )

    # Extract drug information
    drugs = []
    seen_drugs = set()  # Track unique drug names to avoid duplicates

    if result and 'data' in result and 'results' in result['data']:
        results_list = result['data']['results']
        for item in results_list:
            openfda = item.get('openfda', {})

            # Get drug name (brand or generic)
            brand_names = openfda.get('brand_name', [])
            generic_names = openfda.get('generic_name', [])
            drug_name = brand_names[0] if brand_names else (generic_names[0] if generic_names else 'Unknown')

            # Skip duplicates
            if drug_name.upper() in seen_drugs:
                continue
            seen_drugs.add(drug_name.upper())

            # Get manufacturer
            manufacturers = openfda.get('manufacturer_name', [])
            manufacturer = manufacturers[0] if manufacturers else 'Unknown'

            # Get approval date (application_number contains date info)
            app_numbers = openfda.get('application_number', [])
            approval_date = 'Unknown'
            if app_numbers:
                # Try to extract year from application number (format: NDA021778)
                match = re.search(r'(\d{6})', app_numbers[0])
                if match:
                    date_str = match.group(1)
                    # Format: YYMMDD or similar - extract year
                    year = '19' + date_str[:2] if date_str[:2] > '50' else '20' + date_str[:2]
                    approval_date = year

            # Get indications
            indications = item.get('indications_and_usage', [''])[0][:200] + '...' if item.get('indications_and_usage') else 'Not specified'

            drugs.append({
                'drug_name': drug_name,
                'manufacturer': manufacturer,
                'approval_date': approval_date,
                'indications': indications,
                'generic_name': generic_names[0] if generic_names else 'N/A'
            })

    # Sort by drug name
    drugs.sort(key=lambda x: x['drug_name'])

    # Create summary
    summary = f"Found {len(drugs)} FDA-approved drugs for rheumatoid arthritis:\n\n"

    for drug in drugs:
        summary += f"• {drug['drug_name']}"
        if drug['generic_name'] != 'N/A' and drug['generic_name'].lower() != drug['drug_name'].lower():
            summary += f" ({drug['generic_name']})"
        summary += f"\n  Manufacturer: {drug['manufacturer']}\n"
        summary += f"  Approval: {drug['approval_date']}\n"
        summary += f"  Indication: {drug['indications'][:150]}...\n\n"

    return {
        'total_count': len(drugs),
        'drugs': drugs,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_rheumatoid_arthritis_fda_drugs()
    print(f"Total drugs found: {result['total_count']}\n")
    print(result['summary'])
