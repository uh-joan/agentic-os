import sys
sys.path.insert(0, "scripts")
from mcp.servers.fda_mcp import lookup_drug

def get_braf_inhibitor_fda_drugs():
    """Get FDA approved BRAF inhibitor drugs.

    Returns:
        dict: Contains total_count and drugs list with details
    """
    # Known BRAF inhibitors (generic names)
    # Search by specific drug names since "BRAF inhibitor" class term doesn't work in FDA API
    braf_inhibitors = ["dabrafenib", "vemurafenib", "encorafenib"]

    all_drugs = []

    for generic_name in braf_inhibitors:
        result = lookup_drug(
            search_term=generic_name,
            search_type="general",
            count="openfda.brand_name.exact",
            limit=10
        )

        # FDA API returns nested structure: result['data']['results']
        data = result.get('data', {})
        if data and 'results' in data:
            results = data.get('results', [])

            # For count queries, results are aggregated: [{'term': 'TAFINLAR', 'count': 2}, ...]
            for item in results:
                brand_name = item.get('term')
                count = item.get('count', 0)
                if brand_name:
                    all_drugs.append({
                        'brand_name': brand_name,
                        'generic_name': generic_name,
                        'count': count
                    })

    # Sort by count (most common first)
    all_drugs.sort(key=lambda x: x.get('count', 0), reverse=True)

    return {
        'total_count': len(all_drugs),
        'drugs': all_drugs
    }

# Make skill executable standalone
if __name__ == "__main__":
    result = get_braf_inhibitor_fda_drugs()

    print(f"\n{'='*80}")
    print(f"FDA Approved BRAF Inhibitor Drugs")
    print(f"{'='*80}\n")
    print(f"Total drugs found: {result['total_count']}\n")

    if result['total_count'] > 0:
        for i, drug in enumerate(result['drugs'], 1):
            print(f"{i}. {drug.get('brand_name', 'N/A')} ({drug.get('generic_name', 'N/A')})")
            print(f"   FDA record count: {drug.get('count', 'N/A')}")
            print()
    else:
        print("No BRAF inhibitor drugs found in FDA database.")
        if 'error' in result:
            print(f"Error: {result['error']}")
