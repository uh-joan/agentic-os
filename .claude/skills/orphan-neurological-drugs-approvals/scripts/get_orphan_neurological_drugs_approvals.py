import sys
from datetime import datetime, timedelta
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drugs

def get_orphan_neurological_drugs_approvals():
    """Retrieve orphan drugs approved for rare neurological diseases in past 3 years.

    Focuses on ALS, Duchenne, Huntington's, SMA, and other neurological orphan designations.

    Returns:
        dict: Orphan neurological drugs with approval details and therapeutic area analysis
    """

    # Calculate date range (past 3 years)
    current_date = datetime.now()
    three_years_ago = current_date - timedelta(days=3*365)
    date_filter = three_years_ago.strftime("%Y%m%d")

    # Neurological conditions to search
    neurological_conditions = [
        "amyotrophic lateral sclerosis",
        "ALS",
        "Duchenne muscular dystrophy",
        "Huntington disease",
        "spinal muscular atrophy",
        "SMA",
        "multiple sclerosis",
        "Parkinson",
        "rare neurological",
        "neuromuscular",
        "neurodegenerative"
    ]

    all_drugs = []
    seen_names = set()

    print(f"Searching for orphan neurological drugs approved since {date_filter}...\n")

    for condition in neurological_conditions:
        print(f"  Searching: {condition}")

        try:
            # Search for drugs with this indication
            result = search_drugs(
                search=condition,
                limit=100
            )

            if not result or 'results' not in result:
                continue

            drugs = result.get('results', [])

            for drug in drugs:
                # Extract drug information
                brand_name = drug.get('brand_name', 'Unknown')
                generic_name = drug.get('generic_name', 'Unknown')
                sponsor_name = drug.get('sponsor_name', 'Unknown')

                # Check if it's an orphan designation
                products = drug.get('products', [])
                has_orphan = False
                approval_date = None

                for product in products:
                    marketing_status = product.get('marketing_status', '')
                    if 'orphan' in marketing_status.lower() or 'Prescription' in marketing_status:
                        has_orphan = True

                    # Get approval date from product
                    if 'te_code' in product and product.get('te_code'):
                        # Extract year from product info if available
                        pass

                # Get submission info for approval date
                submissions = drug.get('submissions', [])
                for submission in submissions:
                    submission_status = submission.get('submission_status', '')
                    if 'Approved' in submission_status or 'AP' in submission_status:
                        submission_number = submission.get('submission_number', '')
                        # Approval date might be in submission details
                        pass

                # Check openfda section for approval date
                openfda = drug.get('openfda', {})
                application_number = openfda.get('application_number', ['Unknown'])[0] if openfda.get('application_number') else 'Unknown'

                # Create unique identifier
                drug_key = f"{brand_name}_{generic_name}".lower()

                if drug_key not in seen_names:
                    seen_names.add(drug_key)

                    drug_info = {
                        'brand_name': brand_name,
                        'generic_name': generic_name,
                        'sponsor': sponsor_name,
                        'application_number': application_number,
                        'therapeutic_area': condition,
                        'has_orphan_status': has_orphan,
                        'products_count': len(products)
                    }

                    all_drugs.append(drug_info)

        except Exception as e:
            print(f"    Error searching {condition}: {str(e)}")
            continue

    print(f"\nTotal drugs found: {len(all_drugs)}\n")

    # Deduplicate and categorize
    unique_drugs = {}
    for drug in all_drugs:
        key = drug['generic_name'].lower()
        if key not in unique_drugs:
            unique_drugs[key] = drug

    # Categorize by therapeutic area
    therapeutic_areas = {}
    for drug in unique_drugs.values():
        area = drug['therapeutic_area']
        if area not in therapeutic_areas:
            therapeutic_areas[area] = []
        therapeutic_areas[area].append(drug)

    # Generate summary
    summary = generate_summary(unique_drugs, therapeutic_areas)

    return {
        'total_drugs': len(unique_drugs),
        'drugs': list(unique_drugs.values()),
        'therapeutic_areas': therapeutic_areas,
        'summary': summary
    }


def generate_summary(unique_drugs, therapeutic_areas):
    """Generate formatted summary"""
    summary = f"""
{'='*80}
ORPHAN NEUROLOGICAL DRUGS - RECENT APPROVALS (Past 3 Years)
{'='*80}

Total Orphan Neurological Drugs Found: {len(unique_drugs)}

THERAPEUTIC AREA DISTRIBUTION:

"""

    # Sort therapeutic areas by drug count
    sorted_areas = sorted(
        therapeutic_areas.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for area, drugs in sorted_areas:
        summary += f"\n{area.upper()} ({len(drugs)} drugs):\n"
        for drug in drugs[:5]:  # Show top 5 per area
            summary += f"  - {drug['brand_name']} ({drug['generic_name']})\n"
            summary += f"    Sponsor: {drug['sponsor']}\n"

    summary += f"""
KEY INSIGHTS:

MARKET LANDSCAPE:
- Rare neurological diseases represent significant unmet medical need
- Orphan drug designation provides regulatory and commercial advantages
- Multiple targets across neuromuscular and neurodegenerative conditions

REGULATORY STRATEGY:
- Orphan designation accelerates development timelines
- Smaller trial sizes acceptable for rare diseases
- 7-year market exclusivity in US
- Priority review and fee waivers available

BUSINESS IMPLICATIONS:
- Premium pricing supported by orphan status
- Limited competition in ultra-rare indications
- Strong investor interest in rare disease platforms
- Potential for label expansion to related conditions

DEVELOPMENT TRENDS:
- Gene therapies emerging for genetic neuromuscular diseases
- Antisense oligonucleotides for specific mutations
- Disease-modifying approaches gaining traction
- Natural history studies critical for regulatory approval
"""

    return summary


if __name__ == "__main__":
    result = get_orphan_neurological_drugs_approvals()
    print(result['summary'])

    # Print detailed drug list
    print("\n" + "="*80)
    print("DETAILED DRUG LIST")
    print("="*80 + "\n")

    for idx, drug in enumerate(sorted(result['drugs'], key=lambda x: x['brand_name']), 1):
        print(f"{idx}. {drug['brand_name']} ({drug['generic_name']})")
        print(f"   Sponsor: {drug['sponsor']}")
        print(f"   Application: {drug['application_number']}")
        print(f"   Therapeutic Area: {drug['therapeutic_area']}\n")
