import sys
sys.path.insert(0, ".claude")
from datetime import datetime
from mcp.servers.pubmed_mcp import search_keywords
import re
from collections import Counter

def get_anti_amyloid_publications():
    """Search PubMed for recent publications on anti-amyloid antibodies for Alzheimer's disease.

    Focuses on major antibodies (lecanemab, donanemab, aducanumab, gantenerumab) and
    analyzes publication trends, author institutions, and ARIA safety reporting.

    Returns:
        dict: Contains total_count, publications_by_drug, top_institutions, aria_mentions, and summary
    """

    # Search for anti-amyloid antibody publications using temporal chunking
    # Workaround for PubMed MCP pagination limitation
    base_query = '(lecanemab OR donanemab OR aducanumab OR gantenerumab OR "anti-amyloid antibody" OR "anti-amyloid antibodies") AND (Alzheimer OR "Alzheimer\'s disease")'

    # Define time periods to query (avoids MCP result count limitation)
    # Chunk by year to get comprehensive results
    time_periods = [
        ("2019", "2019"),
        ("2020", "2020"),
        ("2021", "2021"),
        ("2022", "2022"),
        ("2023", "2023"),
        ("2024", "2024"),
        ("2025", "2025")  # Include current year
    ]

    all_results = []
    seen_pmids = set()  # Deduplicate by PMID

    print(f"Searching PubMed with temporal chunking to maximize results...")
    print(f"Base query: {base_query}\n")

    for start_year, end_year in time_periods:
        # Build date-specific query
        date_query = f'{base_query} AND ("{start_year}"[Date - Publication] : "{end_year}"[Date - Publication])'

        print(f"Fetching {start_year} publications...")

        try:
            # Request moderate batch size (PubMed MCP may return fewer)
            result = search_keywords(keywords=date_query, num_results=100)

            if not result:
                print(f"  No results for {start_year}")
                continue

            # Handle both response formats
            if isinstance(result, list):
                articles = result
            else:
                articles = result.get('articles', [])

            if not articles:
                print(f"  No articles returned for {start_year}")
                continue

            # Deduplicate by PMID
            new_articles = 0
            for article in articles:
                pmid = article.get('pmid', '')
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    all_results.append(article)
                    new_articles += 1

            print(f"  Added {new_articles} new articles ({len(articles)} total in batch)")

            # Brief delay to avoid rate limiting (100ms)
            import time
            time.sleep(0.1)

        except Exception as e:
            print(f"  Error fetching {start_year}: {e}")
            continue

    total_count = len(all_results)
    print(f"\nTotal unique publications found: {total_count} (across {len(time_periods)} time periods)")
    print(f"De-duplicated {len(seen_pmids)} unique PMIDs\n")

    # Analyze publications by drug
    drug_mentions = {
        'lecanemab': 0,
        'donanemab': 0,
        'aducanumab': 0,
        'gantenerumab': 0,
        'general_anti_amyloid': 0
    }

    # Analyze ARIA mentions and institutions
    aria_count = 0
    institutions = []
    year_distribution = Counter()

    for article in all_results:
        # Safely extract and convert title/abstract to strings
        title_raw = article.get('title', '')
        abstract_raw = article.get('abstract', '')

        # Handle cases where title/abstract might not be strings
        title = str(title_raw).lower() if title_raw else ''
        abstract = str(abstract_raw).lower() if abstract_raw else ''

        combined_text = f"{title} {abstract}"

        # Count drug mentions
        if 'lecanemab' in combined_text:
            drug_mentions['lecanemab'] += 1
        if 'donanemab' in combined_text:
            drug_mentions['donanemab'] += 1
        if 'aducanumab' in combined_text:
            drug_mentions['aducanumab'] += 1
        if 'gantenerumab' in combined_text:
            drug_mentions['gantenerumab'] += 1
        if 'anti-amyloid' in combined_text and not any(drug in combined_text for drug in ['lecanemab', 'donanemab', 'aducanumab', 'gantenerumab']):
            drug_mentions['general_anti_amyloid'] += 1

        # Check for ARIA mentions
        if 'aria' in combined_text or 'amyloid-related imaging abnormalities' in combined_text:
            aria_count += 1

        # Extract institutions from authors
        authors = article.get('authors', [])
        if isinstance(authors, list):
            for author in authors:
                # Authors might be strings or dicts
                if isinstance(author, dict):
                    affiliation = author.get('affiliation', '')
                    if affiliation:
                        institutions.append(affiliation)
                elif isinstance(author, str) and ',' in author:
                    # Sometimes author format is "Name, Institution"
                    parts = author.split(',', 1)
                    if len(parts) > 1:
                        institutions.append(parts[1].strip())

        # Also check for affiliation field at article level
        if 'affiliation' in article:
            institutions.append(article['affiliation'])

        # Count by publication year
        pub_date = article.get('publication_date', '')
        if pub_date:
            # Extract year from date string (format: YYYY-MM-DD or YYYY)
            year_match = re.match(r'(\d{4})', pub_date)
            if year_match:
                year = year_match.group(1)
                year_distribution[year] += 1

    # Analyze top institutions
    institution_counts = Counter()
    for inst in institutions:
        if inst:
            # Clean and count institutions
            clean_inst = inst.split(',')[0].strip()  # Take first part before comma
            if len(clean_inst) > 10:  # Filter out too-short strings
                institution_counts[clean_inst] += 1

    top_institutions = institution_counts.most_common(10)

    # Calculate ARIA reporting rate
    aria_percentage = (aria_count / total_count * 100) if total_count > 0 else 0

    # Prepare summary
    summary = {
        'total_publications': total_count,
        'date_range': '2019-2024',
        'publications_by_drug': drug_mentions,
        'aria_safety_reporting': {
            'articles_mentioning_aria': aria_count,
            'percentage_of_total': round(aria_percentage, 1)
        },
        'top_institutions': [{'institution': inst, 'publication_count': count} for inst, count in top_institutions],
        'publications_by_year': dict(sorted(year_distribution.items(), reverse=True)),
        'key_insights': [
            f"Most studied drug: {max(drug_mentions, key=drug_mentions.get)} ({drug_mentions[max(drug_mentions, key=drug_mentions.get)]} publications)",
            f"ARIA safety data reported in {aria_percentage:.1f}% of publications",
            f"Peak publication year: {max(year_distribution, key=year_distribution.get) if year_distribution else 'N/A'} ({year_distribution.get(max(year_distribution, key=year_distribution.get, default=''), 0)} articles)"
        ]
    }

    # Print detailed summary
    print("\n" + "="*80)
    print("ANTI-AMYLOID ANTIBODY PUBLICATIONS ANALYSIS (2019-2024)")
    print("="*80)
    print(f"\nTotal Publications: {total_count}")
    print(f"Search Strategy: Temporal chunking (2019-2025, year-by-year queries)")
    print(f"Base Query: {base_query}")

    print("\n--- Publications by Drug ---")
    for drug, count in sorted(drug_mentions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {drug.replace('_', ' ').title()}: {count}")

    print("\n--- ARIA Safety Reporting ---")
    print(f"  Articles mentioning ARIA: {aria_count} ({aria_percentage:.1f}%)")

    print("\n--- Top 10 Research Institutions ---")
    for i, (inst, count) in enumerate(top_institutions, 1):
        print(f"  {i}. {inst}: {count} publications")

    print("\n--- Publications by Year ---")
    for year, count in sorted(year_distribution.items(), reverse=True):
        print(f"  {year}: {count}")

    print("\n--- Key Insights ---")
    for insight in summary['key_insights']:
        print(f"  • {insight}")

    print("\n" + "="*80)

    return {
        'data': {
            'total_count': total_count,
            'analysis': summary,
            'raw_results': all_results[:50]  # Return first 50 for reference
        },
        'source_metadata': {
            'source': 'PubMed',
            'mcp_server': 'pubmed_mcp',
            'query_date': datetime.now().strftime('%Y-%m-%d'),
            'query_params': {
                'keywords': base_query,
                'time_periods': time_periods,
                'num_results_per_period': 100
            },
            'data_count': total_count,
            'data_type': 'publications'
        },
        'summary': f"Found {total_count} anti-amyloid antibody publications (2019-2024) with {aria_count} mentioning ARIA safety ({aria_percentage:.1f}%) (source: PubMed, {datetime.now().strftime('%Y-%m-%d')})"
    }

if __name__ == "__main__":
    import json
    result = get_anti_amyloid_publications()

    # For human-readable output (comment out for JSON verification)
    # print(f"\n✓ Analysis complete. {result['data']['total_count']} publications analyzed.")

    # For JSON verification (required by verify_source_attribution.py)
    print(json.dumps(result, indent=2))
