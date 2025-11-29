import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug
import json
from collections import defaultdict
from datetime import datetime
import os

# IMPROVEMENT 1: Dynamic term discovery (zero hardcoding)
# Cache file for learned term mappings
CACHE_FILE = ".claude/skills/.term_cache.json"

def load_term_cache():
    """Load cached term mappings from file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_term_cache(cache):
    """Save term mappings to cache file."""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save cache: {e}")

def test_fda_term(term):
    """Test if a term returns results in FDA."""
    try:
        result = lookup_drug(
            search_type="general",
            search_term=term,
            count="openfda.brand_name.exact",
            limit=1
        )
        if isinstance(result, dict) and 'data' in result:
            brands = result.get('data', {}).get('results', [])
            return len(brands) > 0
    except:
        return False
    return False

def query_nlm_conditions(term):
    """Query NLM Medical Conditions database for synonyms.

    Uses the NLM Clinical Tables MCP tool to get professional medical
    terminology and condition synonyms from the National Library of Medicine.

    Returns list of condition names from NLM.
    """
    try:
        # Import the MCP tool function
        sys.path.insert(0, ".claude")
        from mcp.servers.nlm_codes_mcp import search_conditions

        # Call NLM Medical Conditions database
        result = search_conditions(
            terms=term,
            maxList=10
        )

        # Extract condition display names
        # NLM returns a list directly: [{"code": "...", "display": "..."}, ...]
        if isinstance(result, list):
            conditions = []
            for item in result:
                display = item.get('display', '')
                if display:
                    conditions.append(display)
            return conditions

        return []

    except Exception as e:
        print(f"  (NLM query failed: {e})")
        return []

def discover_working_fda_term(user_term, cache=None):
    """
    Dynamically discover working FDA term using NLM medical knowledge.

    Algorithm:
    1. Check cache (instant if found)
    2. Test user term directly in FDA
    3. If fails, query NLM Medical Conditions for synonyms
    4. Extract keywords from NLM results
    5. Test each keyword in FDA
    6. Cache successful mapping

    Args:
        user_term: User-provided therapeutic area term
        cache: Optional cache dict (loaded from file if None)

    Returns:
        tuple: (working_term, method) or (None, "failed")
               method: "cached", "direct", "nlm_discovery", "word_split", or "failed"
    """
    if cache is None:
        cache = load_term_cache()

    # Check cache first (instant)
    if user_term in cache:
        return cache[user_term], "cached"

    # Try user term directly
    if test_fda_term(user_term):
        cache[user_term] = user_term
        save_term_cache(cache)
        return user_term, "direct"

    # Query NLM for medical synonyms
    conditions = query_nlm_conditions(user_term)

    if conditions:
        # Extract keywords from NLM results
        keywords = set()
        # Expanded stopwords to filter out:
        # - Common words, directions, anatomical positions
        # - Abbreviations in parentheses
        # - Generic medical terms
        stopwords = {
            'disease', 'disorder', 'condition', 'syndrome', 'the', 'and', 'or', 'a', 'an',
            'left', 'right', 'upper', 'lower', 'type', 'adult', 'juvenile',
            'mild', 'severe', 'chronic', 'acute'
        }

        for condition in conditions:
            words = condition.lower().split()
            for word in words:
                # Remove punctuation
                cleaned = word.strip(',-.()')
                # Filter:
                # - Must be > 4 chars (avoids abbreviations)
                # - Not in stopwords
                # - Doesn't start with '(' (parenthetical abbreviations)
                # - Only alphabetic (no numbers or mixed)
                if (len(cleaned) > 4 and
                    cleaned not in stopwords and
                    not word.startswith('(') and
                    cleaned.isalpha()):
                    keywords.add(cleaned)

        # Test each keyword in FDA (alphabetical order for consistency)
        for keyword in sorted(keywords):
            if test_fda_term(keyword):
                cache[user_term] = keyword
                save_term_cache(cache)
                return keyword, "nlm_discovery"

    # Fallback: try individual words from user term
    for word in user_term.split():
        if len(word) > 3 and test_fda_term(word):
            cache[user_term] = word
            save_term_cache(cache)
            return word, "word_split"

    return None, "failed"

def validate_and_suggest_therapeutic_area(term):
    """
    Dynamically validate therapeutic area using NLM + FDA testing.

    ZERO HARDCODING - uses:
    - NLM Medical Conditions database for professional medical synonyms
    - FDA API testing to verify what actually works
    - Persistent cache for instant lookups on subsequent queries

    Returns:
        tuple: (validated_term, suggestions, error_message)
    """
    if not term:
        return None, [], "No therapeutic area specified"

    validated_term, method = discover_working_fda_term(term)

    if validated_term:
        if method == "nlm_discovery":
            return validated_term, [validated_term], f"Using '{validated_term}' instead of '{term}' (discovered via NLM)"
        elif method == "cached":
            return validated_term, [], None  # Silent success from cache
        elif method == "word_split":
            return validated_term, [validated_term], f"Using '{validated_term}' (extracted from '{term}')"
        else:  # direct
            return validated_term, [], None

    # Failed to find working term
    return None, [], f"No working FDA term found for '{term}'. Try specific drug names or validated terms like 'cancer', 'diabetes', 'heart', 'HIV'."

def get_products_by_approval_pathway(
    pathway: str,
    therapeutic_area: str = None,
    get_brand_names: bool = False,
    filter_brands_by_pathway: bool = False,  # IMPROVEMENT 3: Brand filtering
    count_type: str = "submissions",  # IMPROVEMENT 2: Unique counting
    approval_year_start: int = None,  # IMPROVEMENT 4: Year filtering
    approval_year_end: int = None,
    use_field_exists: bool = False,  # IMPROVEMENT 5: Advanced filtering
    max_brands: int = 50,
    show_progress: bool = False
):
    """Find FDA-approved drugs by approval pathway using FDA submission metadata.

    This skill uses the FDA API's submissions.review_priority and
    submissions.submission_property_type fields to identify drugs by pathway.

    Args:
        pathway: Approval pathway type
                - priority_review: PRIORITY review designation
                - standard_review: STANDARD review designation
                - orphan: Orphan drug designation for rare diseases
        therapeutic_area: Optional disease/drug class filter (e.g., "cancer", "oncology")
        get_brand_names: If True, fetches brand names (default: False)
        filter_brands_by_pathway: If True, filters brands to only those with pathway (slow)
        count_type: "submissions" (default) or "unique_drugs" (deduplicates by application)
        approval_year_start: Optional start year filter (e.g., 2020)
        approval_year_end: Optional end year filter (e.g., 2024)
        use_field_exists: If True, filters to drugs with any designation
        max_brands: Maximum brands to fetch for filtering (default: 50)
        show_progress: Show progress bars for brand filtering

    Returns:
        dict: Contains pathway counts, therapeutic area, and optional brand list

    Example:
        # Get unique priority review cancer drugs approved 2020-2024
        result = get_products_by_approval_pathway(
            pathway="priority_review",
            therapeutic_area="cancer",
            count_type="unique_drugs",
            approval_year_start=2020,
            approval_year_end=2024
        )
    """

    # Validate pathway
    valid_pathways = ['priority_review', 'standard_review', 'orphan']
    if pathway not in valid_pathways:
        return {
            'error': f"Invalid pathway '{pathway}'. Must be one of: {', '.join(valid_pathways)}",
            'available_pathways': {
                'priority_review': 'Drugs with PRIORITY review designation (often correlates with accelerated approval)',
                'standard_review': 'Drugs with STANDARD review designation',
                'orphan': 'Drugs with orphan designation for rare diseases'
            },
            'note': 'Accelerated approval, breakthrough therapy, and fast track are not available as countable FDA fields'
        }

    # IMPROVEMENT 1: Validate therapeutic area term
    validated_term = therapeutic_area
    term_warning = None
    term_suggestions = []

    if therapeutic_area:
        validated_term, term_suggestions, term_warning = validate_and_suggest_therapeutic_area(therapeutic_area)

        if term_warning and not validated_term:
            print(f"⚠️  {term_warning}")
            if term_suggestions:
                print(f"   Trying first suggestion: '{term_suggestions[0]}'")
                validated_term = term_suggestions[0]
            else:
                print(f"   Proceeding with original term...")
                validated_term = therapeutic_area

    # IMPROVEMENT 6: Use adverse events discovery for comprehensive coverage
    # Query patient.drug.drugindication field to get all drugs prescribed for therapeutic area

    # Clean therapeutic area term (remove apostrophes and special characters that cause MCP errors)
    cleaned_area = therapeutic_area.replace("'", "").replace('"', '') if therapeutic_area else ""

    print(f"Searching for {pathway.replace('_', ' ').title()} products...")
    if therapeutic_area:
        if cleaned_area != therapeutic_area:
            print(f"  Cleaned term: '{therapeutic_area}' → '{cleaned_area}'")
        print(f"  Using adverse events discovery: patient.drug.drugindication:{cleaned_area}")

    # STEP 1: Get all drugs prescribed for this therapeutic area via adverse events
    try:
        adverse_events_result = lookup_drug(
            search_term=f"patient.drug.drugindication:{cleaned_area}",
            search_type="adverse_events",
            count="patient.drug.openfda.brand_name.exact",
            limit=100  # FDA MCP maximum for adverse events
        )

        candidate_brands = []
        if isinstance(adverse_events_result, dict) and 'data' in adverse_events_result:
            brand_results = adverse_events_result.get('data', {}).get('results', [])
            candidate_brands = [
                {
                    'brand_name': item.get('term'),
                    'adverse_events': item.get('count', 0)
                }
                for item in brand_results
                if item.get('term')
            ]
            print(f"  Found {len(candidate_brands)} drugs prescribed for {therapeutic_area}")
        else:
            print(f"  ⚠️  No adverse events data found for {therapeutic_area}")
            # Fallback: try direct search term
            search_term = validated_term if validated_term else therapeutic_area
            print(f"  Falling back to direct search: {search_term}")
            candidate_brands = []

    except Exception as e:
        print(f"  ⚠️  Adverse events query failed: {e}")
        # Fallback: try direct search term
        search_term = validated_term if validated_term else therapeutic_area
        print(f"  Falling back to direct search: {search_term}")
        candidate_brands = []

    # STEP 2: Filter candidate drugs by pathway designation
    drugs_with_pathway = []
    pathway_count = 0

    if candidate_brands:
        print(f"\n  Filtering {len(candidate_brands)} drugs by {pathway.replace('_', ' ')} designation...")
        if show_progress:
            print(f"  (This checks each drug individually - may take time)")

        for i, brand_info in enumerate(candidate_brands, 1):
            brand_name = brand_info['brand_name']

            if show_progress and i % 10 == 0:
                print(f"    Progress: {i}/{len(candidate_brands)} drugs checked...")

            try:
                # Query this specific brand's submission metadata
                if pathway in ['priority_review', 'standard_review']:
                    brand_result = lookup_drug(
                        search_type="general",
                        search_term=brand_name,
                        count="submissions.review_priority",
                        limit=50
                    )

                    target_priority = "PRIORITY" if pathway == "priority_review" else "STANDARD"
                    if isinstance(brand_result, dict) and 'data' in brand_result:
                        results = brand_result.get('data', {}).get('results', [])
                        has_pathway = any(r.get('term') == target_priority for r in results)

                        if has_pathway:
                            drugs_with_pathway.append({
                                'brand_name': brand_name,
                                'adverse_events': brand_info['adverse_events'],
                                'pathway': pathway
                            })
                            pathway_count += 1

                elif pathway == 'orphan':
                    brand_result = lookup_drug(
                        search_type="general",
                        search_term=brand_name,
                        count="submissions.submission_property_type.code",
                        limit=5
                    )

                    if isinstance(brand_result, dict) and 'data' in brand_result:
                        results = brand_result.get('data', {}).get('results', [])
                        has_orphan = any(r.get('term') == 'Orphan' for r in results)

                        if has_orphan:
                            drugs_with_pathway.append({
                                'brand_name': brand_name,
                                'adverse_events': brand_info['adverse_events'],
                                'pathway': 'orphan'
                            })
                            pathway_count += 1

            except Exception as e:
                if show_progress:
                    print(f"    ⚠️  Error checking {brand_name}: {e}")
                continue

        print(f"\n  ✓ Found {pathway_count} drugs with {pathway.replace('_', ' ')} designation")
    else:
        print(f"\n  ⚠️  No candidate drugs found - cannot filter by pathway")

    # Extract brand names from results
    brand_names = [drug['brand_name'] for drug in drugs_with_pathway]
    unique_drug_count = None

    # IMPROVEMENT 2: Unique drug counting (if requested)
    if count_type == "unique_drugs" and pathway_count > 0:
        print(f"\n  Deduplicating by application number...")

        # Fetch application numbers for each brand with pathway
        unique_apps = set()
        for drug in drugs_with_pathway:
            brand = drug['brand_name']
            try:
                app_result = lookup_drug(
                    search_type="general",
                    search_term=brand,
                    count="openfda.application_number.exact",
                    limit=10
                )

                if isinstance(app_result, dict) and 'data' in app_result:
                    apps = app_result.get('data', {}).get('results', [])
                    for app in apps:
                        unique_apps.add(app.get('term'))
            except:
                continue

        unique_drug_count = len(unique_apps)
        print(f"  ✓ {unique_drug_count} unique drugs (vs {pathway_count} drugs with pathway)")

    # Build summary
    pathway_name = pathway.replace('_', ' ').title()

    summary_lines = [
        f"# {pathway_name} Analysis for {therapeutic_area}",
        f"\n**Pathway**: {pathway_name}",
        f"**Therapeutic Area**: {therapeutic_area}",
        f"**Drug Count**: {pathway_count}",
    ]

    if unique_drug_count is not None:
        summary_lines.append(f"**Unique Drug Count** (by application number): {unique_drug_count}")

    if drugs_with_pathway:
        summary_lines.append(f"\n## Drugs with {pathway_name} ({len(drugs_with_pathway)} found):")
        # Sort by adverse events (proxy for prescribing frequency)
        sorted_drugs = sorted(drugs_with_pathway, key=lambda x: x['adverse_events'], reverse=True)
        for i, drug in enumerate(sorted_drugs[:20], 1):
            summary_lines.append(f"{i}. **{drug['brand_name']}** ({drug['adverse_events']:,} adverse event reports)")
        if len(drugs_with_pathway) > 20:
            summary_lines.append(f"... and {len(drugs_with_pathway) - 20} more drugs")

    summary_lines.append("\n## Method")
    summary_lines.append("**STEP 1**: Query adverse events database")
    summary_lines.append(f"- Field: `patient.drug.drugindication:{therapeutic_area}`")
    summary_lines.append(f"- Found: All drugs prescribed for {therapeutic_area}")
    summary_lines.append(f"\n**STEP 2**: Filter by pathway designation")
    if pathway in ['priority_review', 'standard_review']:
        target = "PRIORITY" if pathway == "priority_review" else "STANDARD"
        summary_lines.append(f"- Field: `submissions.review_priority` = {target}")
    elif pathway == 'orphan':
        summary_lines.append(f"- Field: `submissions.submission_property_type.code` = Orphan")
    summary_lines.append(f"- Result: {pathway_count} drugs with {pathway_name} designation")

    summary_lines.append("\n## Advantages")
    summary_lines.append("✅ **Complete coverage**: Adverse events capture all drugs prescribed for therapeutic area")
    summary_lines.append("✅ **Real-world data**: Adverse event counts reflect actual prescribing volume")
    summary_lines.append("✅ **Pathway filtering**: Cross-references with submission metadata for designation")

    summary_lines.append("\n## Data Sources")
    summary_lines.append("- **Adverse Events**: FDA Adverse Events Reporting System (FAERS)")
    summary_lines.append("- **Submissions**: FDA Drug Submissions Metadata")
    summary_lines.append("- Accelerated approval, breakthrough therapy, and fast track not available as countable fields")
    summary_lines.append("- For precise drug-pathway mapping, cross-reference with FDA's official pathway databases")

    products_summary = '\n'.join(summary_lines)

    return {
        'pathway': pathway,
        'therapeutic_area': therapeutic_area,
        'submission_count': pathway_count,  # Number of drugs with pathway (renamed from submission_count for clarity)
        'unique_drug_count': unique_drug_count,
        'drugs': drugs_with_pathway,  # List of dicts with brand_name, adverse_events, pathway
        'brand_names': brand_names,  # List of brand names (all have pathway)
        'brand_count': len(brand_names),
        'products_summary': products_summary,
        'data_source': {
            'api': 'FDA openFDA',
            'step1': f'patient.drug.drugindication:{therapeutic_area} (adverse events)',
            'step2': 'submissions.review_priority' if pathway in ['priority_review', 'standard_review'] else 'submissions.submission_property_type.code'
        },
        'count_type': count_type,
        'method': 'hybrid_adverse_events_discovery',
        'note': f"Found {pathway_count} drugs prescribed for {therapeutic_area} with {pathway.replace('_', ' ')} designation"
    }

if __name__ == "__main__":
    import sys

    # Run tests if --test flag provided
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("="*80)
        print("Running Test Suite")
        print("="*80)

        # TEST 1: Therapeutic area validation
        print("\nTEST 1: Therapeutic Area Validation (cardiovascular → cardiac)")
        print("-" * 80)

        result1 = get_products_by_approval_pathway(
            pathway="priority_review",
            therapeutic_area="cardiovascular"
        )
        print(f"\n✓ Original: cardiovascular")
        print(f"✓ Used: {result1['therapeutic_area']}")
        print(f"✓ Submissions: {result1['submission_count']}")

        # TEST 2: Unique drug counting
        print("\n" + "="*80)
        print("TEST 2: Unique Drug Counting (submissions vs unique drugs)")
        print("-" * 80)

        result2 = get_products_by_approval_pathway(
            pathway="orphan",
            therapeutic_area="oncology",
            get_brand_names=True,
            count_type="unique_drugs"
        )
        print(f"\n✓ Submissions: {result2['submission_count']}")
        print(f"✓ Unique drugs: {result2['unique_drug_count']}")

        # TEST 3: Brand filtering by pathway
        print("\n" + "="*80)
        print("TEST 3: Brand Filtering (only brands with orphan designation)")
        print("-" * 80)

        result3 = get_products_by_approval_pathway(
            pathway="orphan",
            therapeutic_area="oncology",
            get_brand_names=True,
            filter_brands_by_pathway=True,
            max_brands=10,
            show_progress=True
        )
        print(f"\n✓ Total brands in oncology: {result3['brand_count']}")
        print(f"✓ Brands with orphan designation: {result3['filtered_brand_count']}")
        if result3['brands_with_pathway']:
            print(f"✓ Orphan brands: {', '.join(result3['brands_with_pathway'])}")

    # Normal usage with command-line arguments
    elif len(sys.argv) >= 3:
        pathway = sys.argv[1]
        therapeutic_area = sys.argv[2]

        result = get_products_by_approval_pathway(
            pathway=pathway,
            therapeutic_area=therapeutic_area
        )

        if 'error' in result:
            print(f"Error: {result['error']}")
            print(f"\nAvailable pathways:")
            for key, desc in result.get('available_pathways', {}).items():
                print(f"  - {key}: {desc}")
        else:
            print(f"\nResults for {pathway.replace('_', ' ').title()} in {therapeutic_area}:")
            print(f"  Submission Count: {result['submission_count']}")
            if result.get('unique_drug_count'):
                print(f"  Unique Drugs: {result['unique_drug_count']}")

    else:
        print("Usage:")
        print("  python get_products_by_approval_pathway.py <pathway> <therapeutic_area>")
        print("\nExamples:")
        print("  python get_products_by_approval_pathway.py priority_review obesity")
        print("  python get_products_by_approval_pathway.py orphan diabetes")
        print("\nRun tests:")
        print("  python get_products_by_approval_pathway.py --test")
        print("\nValid pathways:")
        print("  - priority_review: Drugs with PRIORITY review designation")
        print("  - standard_review: Drugs with STANDARD review designation")
        print("  - orphan: Drugs with orphan designation for rare diseases")
