import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_articles

def get_crispr_2024_papers():
    """Get CRISPR research papers published in 2024 from PubMed."""
    result = search_articles(term="CRISPR", date_from="2024/01/01", date_to="2024/12/31", max_results=500)
    
    if not result or 'articles' not in result:
        return {'total_count': 0, 'papers': [], 'summary': 'No CRISPR papers found for 2024'}
    
    articles = result.get('articles', [])
    papers = []
    journal_counts = {}
    
    for article in articles:
        paper = {
            'pmid': article.get('pmid', 'N/A'),
            'title': article.get('title', 'N/A'),
            'authors': article.get('authors', []),
            'journal': article.get('journal', 'N/A'),
            'pub_date': article.get('pub_date', 'N/A'),
            'doi': article.get('doi', 'N/A')
        }
        papers.append(paper)
        
        journal = paper['journal']
        journal_counts[journal] = journal_counts.get(journal, 0) + 1
    
    top_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    summary = {
        'total_papers': len(papers),
        'date_range': '2024/01/01 to 2024/12/31',
        'top_journals': [{'journal': j, 'count': c} for j, c in top_journals],
        'search_term': 'CRISPR'
    }
    
    return {'total_count': len(papers), 'papers': papers, 'summary': summary}

if __name__ == "__main__":
    result = get_crispr_2024_papers()
    print(f"\nCRISPR 2024 Papers: {result['summary']['total_papers']} total")
    print(f"Top journals: {result['summary']['top_journals'][:3]}")
