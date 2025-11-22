import sys
sys.path.insert(0, ".claude")
from mcp.servers.uspto_patents_mcp import search_patents
from collections import defaultdict

def get_glp1_obesity_patents():
    """Search USPTO patents for GLP-1 receptor agonists in obesity treatment.
    
    Returns:
        dict: Contains total_count, patents data, and summary
    """
    query = "GLP-1 receptor agonist obesity"
    print(f"Searching USPTO patents for: {query}")
    result = search_patents(query=query, limit=100)
    
    if not result or 'patents' not in result:
        return {'total_count': 0, 'patents': [], 'summary': 'No patents found'}
    
    patents = result['patents']
    total_count = result.get('total', len(patents))
    
    assignees = defaultdict(int)
    filing_years = defaultdict(int)
    patent_details = []
    
    for patent in patents:
        assignee = patent.get('assignee', 'Unknown')
        if assignee and assignee != 'Unknown':
            assignees[assignee] += 1
        
        filing_date = patent.get('filingDate', '')
        if filing_date:
            try:
                year = filing_date.split('-')[0]
                filing_years[year] += 1
            except:
                pass
        
        patent_details.append({
            'patent_number': patent.get('patentNumber', 'N/A'),
            'title': patent.get('title', 'N/A'),
            'filing_date': filing_date,
            'assignee': assignee
        })
    
    patent_details.sort(key=lambda x: x['filing_date'] if x['filing_date'] else '0000-00-00', reverse=True)
    
    top_assignees = sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:10]
    filing_trend = sorted(filing_years.items(), key=lambda x: x[0], reverse=True)[:10]
    
    summary = {
        'total_patents': total_count,
        'top_assignees': [{'company': k, 'patent_count': v} for k, v in top_assignees],
        'filing_trend_by_year': [{'year': k, 'count': v} for k, v in filing_trend]
    }
    
    return {'total_count': total_count, 'patents': patent_details, 'summary': summary}

if __name__ == "__main__":
    result = get_glp1_obesity_patents()
    summary = result['summary']
    print(f"\nGLP-1 Obesity Patents: {summary['total_patents']}")
    print("\nTop Assignees:")
    for item in summary['top_assignees'][:5]:
        print(f"  {item['company']}: {item['patent_count']} patents")
