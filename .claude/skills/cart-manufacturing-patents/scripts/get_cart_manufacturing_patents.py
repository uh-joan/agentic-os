import sys
sys.path.insert(0, ".claude")
from mcp.servers.uspto_patents_mcp import search_patents

def get_cart_manufacturing_patents():
    """Get patents related to CAR-T cell manufacturing and production methods.

    Searches USPTO database for patents covering:
    - CAR-T cell manufacturing innovations
    - Production methods and processes
    - Cost-reducing technologies
    - Scalability improvements

    Returns:
        dict: Contains total_count, patents data, and summary
    """
    # Search for CAR-T manufacturing patents
    query = "CAR-T manufacturing OR CAR-T production OR chimeric antigen receptor manufacturing"

    print(f"Searching USPTO for: {query}")
    result = search_patents(query=query, num_results=100)

    if not result or 'patents' not in result:
        return {
            'total_count': 0,
            'patents': [],
            'summary': 'No CAR-T manufacturing patents found'
        }

    patents = result['patents']
    total_count = len(patents)

    # Analyze assignees (companies/institutions)
    assignee_counts = {}
    manufacturing_focus = {
        'cell_culture': 0,
        'scalability': 0,
        'automation': 0,
        'cost_reduction': 0,
        'quality_control': 0
    }

    for patent in patents:
        # Count assignees
        assignee = patent.get('assignee', 'Unknown')
        assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1

        # Analyze manufacturing focus areas
        title = patent.get('title', '').lower()
        abstract = patent.get('abstract', '').lower()
        combined_text = f"{title} {abstract}"

        if 'culture' in combined_text or 'cultivation' in combined_text:
            manufacturing_focus['cell_culture'] += 1
        if 'scale' in combined_text or 'scalable' in combined_text:
            manufacturing_focus['scalability'] += 1
        if 'automat' in combined_text or 'robotic' in combined_text:
            manufacturing_focus['automation'] += 1
        if 'cost' in combined_text or 'efficient' in combined_text:
            manufacturing_focus['cost_reduction'] += 1
        if 'quality' in combined_text or 'control' in combined_text:
            manufacturing_focus['quality_control'] += 1

    # Get top assignees
    top_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Build summary
    summary = f"""
CAR-T Manufacturing Patents Analysis
=====================================

Total Patents Found: {total_count}

Top Patent Assignees:
"""
    for assignee, count in top_assignees:
        summary += f"  • {assignee}: {count} patents\n"

    summary += f"""
Manufacturing Focus Areas:
  • Cell Culture/Cultivation: {manufacturing_focus['cell_culture']} patents
  • Scalability: {manufacturing_focus['scalability']} patents
  • Automation: {manufacturing_focus['automation']} patents
  • Cost Reduction: {manufacturing_focus['cost_reduction']} patents
  • Quality Control: {manufacturing_focus['quality_control']} patents

Business Implications:
  • Technology Licensing: Top assignees hold key manufacturing IP
  • COGS Optimization: {manufacturing_focus['cost_reduction']} patents focus on cost reduction
  • Automation Opportunities: {manufacturing_focus['automation']} patents in automation
"""

    return {
        'total_count': total_count,
        'patents': patents,
        'top_assignees': top_assignees,
        'manufacturing_focus': manufacturing_focus,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_cart_manufacturing_patents()
    print(result['summary'])
