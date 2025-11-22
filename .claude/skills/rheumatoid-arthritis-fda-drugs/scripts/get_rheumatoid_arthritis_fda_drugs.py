import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_rheumatoid_arthritis_fda_drugs():
    """Get all FDA-approved drugs for rheumatoid arthritis using count-first pattern."""
    # Use count-first pattern (MANDATORY per FDA documentation)
    # Note: FDA API has hard limit of 100 results
    result = lookup_drug(
        search_term='rheumatoid arthritis',
        search_type='general',
        count='openfda.brand_name.exact',
        limit=100
    )

    # DEBUG: Print raw result
    import json
    print("DEBUG - Raw FDA result:")
    print(json.dumps(result, indent=2)[:500])

    # FDA response is nested: result['data']['results']
    data = result.get('data', {})
    if not data or 'results' not in data:
        return {'total_count': 0, 'unique_drugs': 0, 'drugs': [], 'summary': 'No RA drugs found'}

    # Parse count results (format: [{'term': 'BRAND_NAME', 'count': N}, ...])
    brand_counts = []
    for item in data['results']:
        brand_name = item.get('term', 'Unknown')
        count = item.get('count', 0)
        brand_counts.append({
            'brand_name': brand_name,
            'occurrence_count': count
        })

    # Sort by occurrence count (most common first)
    sorted_drugs = sorted(brand_counts, key=lambda x: x['occurrence_count'], reverse=True)

    return {
        'total_count': len(sorted_drugs),
        'unique_drugs': len(sorted_drugs),
        'drugs': sorted_drugs,
        'summary': f"{len(sorted_drugs)} unique brand names found for rheumatoid arthritis"
    }

if __name__ == "__main__":
    result = get_rheumatoid_arthritis_fda_drugs()
    print(f"\nRA FDA Drugs: {result['unique_drugs']} unique brand names")
    if result['unique_drugs'] > 0:
        print(f"Top 10 most common:")
        for i, drug in enumerate(result['drugs'][:10], 1):
            print(f"  {i}. {drug['brand_name']} (appears {drug['occurrence_count']} times)")
    else:
        print("No drugs found")
