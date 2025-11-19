import sys
sys.path.insert(0, "scripts")
from mcp.servers.fda_mcp import lookup_drug

def get_kras_inhibitor_fda_drugs():
    """Get all FDA approved KRAS inhibitor drugs.

    Returns:
        dict: Dictionary mapping brand names to drug info
              Format: {brand_name: {'generic': str, 'count': int}}

    Raises:
        ValueError: If no FDA drugs found or validation fails
    """

    # KRAS inhibitors - try different search strategies
    all_brands = {}

    # Strategy 1: Try broad term "KRAS inhibitor"
    try:
        results = lookup_drug(
            search_term="KRAS inhibitor",
            search_type="general",
            count="openfda.brand_name.exact",
            limit=50
        )

        # Parse count results
        if 'data' in results and 'results' in results['data']:
            for item in results['data']['results']:
                brand = item.get('term', 'Unknown')
                count = item.get('count', 0)
                all_brands[brand] = {'generic': 'KRAS inhibitor', 'count': count}
    except Exception:
        pass  # Broad search may not work

    # Strategy 2: Search specific known KRAS inhibitors
    known_kras_drugs = ["sotorasib", "adagrasib", "LUMAKRAS", "KRAZATI"]

    for drug_name in known_kras_drugs:
        try:
            results = lookup_drug(
                search_term=drug_name,
                search_type="general",
                limit=10
            )

            # Parse full results
            for result in results.get('data', {}).get('results', []):
                openfda = result.get('openfda', {})
                brands = openfda.get('brand_name', [])
                generics = openfda.get('generic_name', [])

                for brand in brands:
                    generic = generics[0] if generics else 'Unknown'
                    if brand not in all_brands:
                        all_brands[brand] = {'generic': generic, 'count': 1}
        except Exception:
            continue  # Skip if drug not found

    # Validate at least some drugs found
    if len(all_brands) == 0:
        raise ValueError("No FDA approved KRAS inhibitors found - expected LUMAKRAS and KRAZATI")

    # Validate expected drugs present (known KRAS G12C inhibitors)
    expected_drugs = ['LUMAKRAS', 'KRAZATI']
    found_expected = [drug for drug in expected_drugs if drug in all_brands]
    if len(found_expected) == 0:
        print(f"WARNING: Expected drugs {expected_drugs} not found in results", file=sys.stderr)

    return all_brands

if __name__ == "__main__":
    try:
        result = get_kras_inhibitor_fda_drugs()
        print(f"✓ Data collection successful: {len(result)} FDA approved KRAS inhibitors found")
        print()
        for brand, info in result.items():
            print(f"  {brand}: {info['generic']} ({info['count']} records)")
    except ValueError as e:
        print(f"✗ Data validation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)
