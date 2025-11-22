import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_articles
import json
from collections import Counter

def get_crispr_sickle_cell_publications():
    """Get latest publications on CRISPR gene editing for sickle cell disease.

    Returns:
        dict: Contains total_count, publications data, and analysis summary
    """

    query = '(CRISPR OR "gene editing" OR "genome editing") AND ("sickle cell disease" OR "sickle cell anemia" OR SCD)'

    print(f"Searching PubMed for: {query}")
    print("=" * 80)

    result = search_articles(
        query=query,
        max_results=200,
        sort="date"
    )

    if not result or 'articles' not in result:
        return {
            'total_count': 0,
            'publications': [],
            'summary': 'No publications found'
        }

    articles = result['articles']
    total_count = len(articles)

    years = []
    topics = []
    casgevy_count = 0
    off_target_count = 0
    clinical_count = 0
    recent_highlights = []

    for article in articles:
        pub_date = article.get('publication_date', '')
        if pub_date:
            try:
                year = int(pub_date.split('-')[0])
                years.append(year)
            except:
                pass

        title = article.get('title', '').lower()
        abstract = article.get('abstract', '').lower()
        combined = f"{title} {abstract}"

        if 'casgevy' in combined or 'ctx001' in combined or 'ctx-001' in combined:
            casgevy_count += 1
            topics.append('Casgevy/CTX001')

        if 'off-target' in combined or 'off target' in combined:
            off_target_count += 1
            topics.append('Off-target effects')

        if any(term in combined for term in ['clinical trial', 'patient', 'treatment', 'therapy', 'outcome']):
            clinical_count += 1
            topics.append('Clinical outcomes')

        if pub_date and pub_date.startswith(('2023', '2024')):
            recent_highlights.append({
                'title': article.get('title', 'N/A'),
                'authors': article.get('authors', 'N/A')[:100],
                'journal': article.get('journal', 'N/A'),
                'date': pub_date,
                'pmid': article.get('pmid', 'N/A')
            })

    year_counts = Counter(years)
    year_trend = sorted(year_counts.items(), reverse=True)[:10]

    topic_counts = Counter(topics)
    top_topics = topic_counts.most_common(10)

    summary_parts = [
        f"\n{'=' * 80}",
        f"CRISPR GENE EDITING FOR SICKLE CELL DISEASE - PUBLICATION ANALYSIS",
        f"{'=' * 80}",
        f"\nTotal Publications Found: {total_count}",
        f"\n{'─' * 80}",
        f"\nKEY METRICS:",
        f"  • Casgevy/CTX001 mentions: {casgevy_count} publications",
        f"  • Off-target effects studies: {off_target_count} publications",
        f"  • Clinical outcomes research: {clinical_count} publications",
        f"\n{'─' * 80}",
        f"\nPUBLICATION TRENDS (by year):"
    ]

    for year, count in year_trend:
        summary_parts.append(f"  {year}: {count} publications")

    if top_topics:
        summary_parts.extend([
            f"\n{'─' * 80}",
            f"\nTOP RESEARCH TOPICS:"
        ])
        for topic, count in top_topics:
            summary_parts.append(f"  • {topic}: {count} mentions")

    if recent_highlights:
        summary_parts.extend([
            f"\n{'─' * 80}",
            f"\nRECENT HIGHLIGHTS (2023-2024) - Top 10:"
        ])
        for i, article in enumerate(recent_highlights[:10], 1):
            summary_parts.extend([
                f"\n{i}. {article['title']}",
                f"   Authors: {article['authors']}",
                f"   Journal: {article['journal']}",
                f"   Date: {article['date']} | PMID: {article['pmid']}"
            ])

    summary_parts.extend([
        f"\n{'─' * 80}",
        f"\nBUSINESS CONTEXT:",
        f"  Following Casgevy approval (Dec 2023 - first CRISPR drug)",
        f"  Key assessment areas:",
        f"    - Technology platform maturity",
        f"    - Safety profile (off-target effects)",
        f"    - Clinical efficacy data",
        f"    - Licensing opportunities",
        f"{'=' * 80}\n"
    ])

    summary = '\n'.join(summary_parts)

    return {
        'total_count': total_count,
        'publications': articles,
        'analysis': {
            'casgevy_mentions': casgevy_count,
            'off_target_studies': off_target_count,
            'clinical_studies': clinical_count,
            'year_distribution': dict(year_trend),
            'recent_count_2023_2024': len(recent_highlights)
        },
        'summary': summary
    }

if __name__ == "__main__":
    result = get_crispr_sickle_cell_publications()
    print(result['summary'])

    if result['publications']:
        print("\nSample Publication Data Structure:")
        print("=" * 80)
        sample = result['publications'][0]
        print(json.dumps({k: v for k, v in sample.items() if k in ['title', 'authors', 'journal', 'publication_date', 'pmid', 'abstract']}, indent=2))
