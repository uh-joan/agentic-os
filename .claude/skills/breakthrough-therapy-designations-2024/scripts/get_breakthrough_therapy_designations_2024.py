import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drugs

def get_breakthrough_therapy_designations_2024():
    """Get all drugs with breakthrough therapy designation approved in 2024.

    Breakthrough therapy designation accelerates development and review for
    serious/life-threatening conditions showing substantial improvement over
    existing therapies.

    Returns:
        dict: Contains total_count, drugs list, and summary
    """

    # Search for all recent drug approvals
    # The FDA API may not directly expose breakthrough designation
    # We'll search broadly and filter based on available fields

    try:
        # Try to get recent approvals - use a broad search
        result = search_drugs(
            search="*:*",  # All drugs
            limit=100  # Get sample to understand data structure
        )

        if not result or 'results' not in result:
            return {
                'total_count': 0,
                'drugs': [],
                'summary': 'Unable to retrieve drug data from FDA API'
            }

        # Analyze structure
        drugs_2024 = []
        total_checked = 0

        for drug in result.get('results', []):
            total_checked += 1
            openfda = drug.get('openfda', {})
            products = drug.get('products', [])
            submissions = drug.get('submissions', [])

            # Check if any product was approved in 2024
            has_2024_approval = False
            approval_date = None

            for product in products:
                mkt_status_date = product.get('marketing_status_date', '')
                if mkt_status_date and '2024' in mkt_status_date:
                    has_2024_approval = True
                    approval_date = mkt_status_date
                    break

            if has_2024_approval:
                # Extract drug information
                brand_names = openfda.get('brand_name', [])
                generic_names = openfda.get('generic_name', [])

                brand_name = brand_names[0] if brand_names else 'Unknown'
                generic_name = generic_names[0] if generic_names else 'Unknown'

                sponsor = drug.get('sponsor_name', 'Unknown')
                app_number = drug.get('application_number', 'N/A')

                # Get indication
                indications = openfda.get('indications_and_usage', [])
                indication = indications[0] if indications else 'N/A'
                if len(indication) > 150:
                    indication = indication[:150] + '...'

                # Get mechanism
                moa_list = openfda.get('pharm_class_moa', [])
                mechanism = moa_list[0] if moa_list else 'N/A'

                # Check submission details for breakthrough info
                is_breakthrough = False
                submission_details = []

                for submission in submissions:
                    sub_type = submission.get('submission_type', '')
                    sub_class = submission.get('submission_class_code', '')
                    sub_class_desc = submission.get('submission_class_code_description', '')

                    submission_details.append(f"{sub_type}/{sub_class}")

                    # Look for breakthrough indicators
                    if 'breakthrough' in str(sub_class_desc).lower():
                        is_breakthrough = True

                drug_info = {
                    'brand_name': brand_name,
                    'generic_name': generic_name,
                    'application_number': app_number,
                    'sponsor': sponsor,
                    'approval_date': approval_date,
                    'indication': indication,
                    'mechanism': mechanism,
                    'breakthrough_designated': is_breakthrough,
                    'submission_info': ', '.join(submission_details[:3])
                }

                drugs_2024.append(drug_info)

        # Sort by approval date
        drugs_2024.sort(key=lambda x: x.get('approval_date', ''), reverse=True)

        # Create summary
        total = len(drugs_2024)
        breakthrough_count = sum(1 for d in drugs_2024 if d['breakthrough_designated'])

        summary_lines = [
            f"\n{'='*120}",
            f"FDA DRUG APPROVALS IN 2024 - BREAKTHROUGH THERAPY STATUS",
            f"{'='*120}\n",
            f"Total 2024 approvals found in sample: {total}",
            f"Drugs checked: {total_checked}",
            f"Confirmed breakthrough therapy designations in API: {breakthrough_count}\n",
            f"NOTE: FDA drug labels API may not contain complete breakthrough designation data.",
            f"      For authoritative breakthrough therapy designation list, consult:",
            f"      - FDA's Breakthrough Therapy Designations webpage",
            f"      - FDA drug approval announcements",
            f"      - CenterWatch or FDA RSS feeds\n"
        ]

        if total > 0:
            summary_lines.append(f"{'Brand Name':<25} {'Generic Name':<30} {'Date':<12} {'BT':<4} {'Sponsor':<30}")
            summary_lines.append(f"{'-'*25} {'-'*30} {'-'*12} {'-'*4} {'-'*30}")

            for drug in drugs_2024:
                brand = (drug['brand_name'][:23] + '..') if len(drug['brand_name']) > 25 else drug['brand_name']
                generic = (drug['generic_name'][:28] + '..') if len(drug['generic_name']) > 30 else drug['generic_name']
                date = drug['approval_date'][:10] if drug['approval_date'] else 'N/A'
                bt = 'Yes' if drug['breakthrough_designated'] else 'No'
                sponsor = (drug['sponsor'][:28] + '..') if len(drug['sponsor']) > 30 else drug['sponsor']

                summary_lines.append(f"{brand:<25} {generic:<30} {date:<12} {bt:<4} {sponsor:<30}")

            summary_lines.append(f"\n{'='*120}\n")

            # Detailed information
            summary_lines.append("DETAILED INFORMATION:\n")
            for i, drug in enumerate(drugs_2024, 1):
                summary_lines.append(f"\n{i}. {drug['brand_name']} ({drug['generic_name']})")
                summary_lines.append(f"   Application: {drug['application_number']}")
                summary_lines.append(f"   Sponsor: {drug['sponsor']}")
                summary_lines.append(f"   Approval Date: {drug['approval_date']}")
                summary_lines.append(f"   Breakthrough Designated: {'Yes' if drug['breakthrough_designated'] else 'No (not found in API)'}")
                summary_lines.append(f"   Indication: {drug['indication']}")
                summary_lines.append(f"   Mechanism: {drug['mechanism']}")
                summary_lines.append(f"   Submissions: {drug['submission_info']}")

        summary = '\n'.join(summary_lines)

        return {
            'total_count': total,
            'breakthrough_count': breakthrough_count,
            'drugs': drugs_2024,
            'summary': summary
        }

    except Exception as e:
        return {
            'total_count': 0,
            'drugs': [],
            'summary': f'Error retrieving FDA data: {str(e)}'
        }

if __name__ == "__main__":
    result = get_breakthrough_therapy_designations_2024()
    print(result['summary'])
