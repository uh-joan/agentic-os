import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search
import re
from collections import Counter

def get_anti_amyloid_publications():
    """Search PubMed for recent publications on anti-amyloid antibodies for Alzheimer's disease.

    Focuses on major antibodies (lecanemab, donanemab, aducanumab, gantenerumab) and
    analyzes publication trends, author institutions, and ARIA safety reporting.

    Returns:
        dict: Contains total_count, publications_by_drug, top_institutions, aria_mentions, and summary
    """

    # Search for anti-amyloid antibody publications (last 5 years for recent focus)
    search_query = '(lecanemab OR donanemab OR aducanumab OR gantenerumab OR "anti-amyloid antibody" OR "anti-amyloid antibodies") AND (Alzheimer OR "Alzheimer\'s disease") AND ("2019"[Date - Publication] : "2024"[Date - Publication])'

    print(f"Searching PubMed for: {search_query}")

    # Get results with pagination
    all_results = []
    page_token = None
    page_count = 0
    max_pages = 50  # Limit to prevent excessive API calls

    while page_count < max_pages:
        if page_token:
            result = search(query=search_query, max_results=100, page_token=page_token)
        else:
            result = search(query=search_query, max_results=100)

        if not result or 'results' not in result:
            break

        all_results.extend(result['results'])
        page_count += 1

        # Check for next page
        if 'next_page_token' in result and result['next_page_token']:
            page_token = result['next_page_token']
            print(f"  Retrieved page {page_count}, total articles so far: {len(all_results)}")
        else:
            break

    total_count = len(all_results)
    print(f"\nTotal publications found: {total_count}")

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
        title = article.get('title', '').lower()
        abstract = article.get('abstract', '').lower()
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
        for author in authors:
            if isinstance(author, dict) and 'affiliation' in author:
                institutions.append(author['affiliation'])

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
    print(f"Search Query: {search_query}")

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
        'total_count': total_count,
        'summary': summary,
        'raw_results': all_results[:50]  # Return first 50 for reference
    }

if __name__ == "__main__":
    result = get_anti_amyloid_publications()
    print(f"\n✓ Analysis complete. {result['total_count']} publications analyzed.")
