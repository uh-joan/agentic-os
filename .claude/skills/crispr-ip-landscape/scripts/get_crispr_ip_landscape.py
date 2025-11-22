import sys
sys.path.insert(0, ".claude")
from mcp.servers.uspto_patents_mcp import search_patents
import re
from collections import defaultdict

def get_crispr_ip_landscape():
    """Map CRISPR patent landscape across institutions and commercial entities.

    Analyzes patents from:
    - Academic: Broad Institute, UC Berkeley
    - Commercial: Editas Medicine, CRISPR Therapeutics, Intellia Therapeutics

    Returns:
        dict: Contains total patents, assignee breakdown, patent families, geographic coverage
    """

    # Define key entities to track
    academic_entities = {
        'Broad Institute': ['Broad Institute', 'Massachusetts Institute of Technology', 'MIT', 'Harvard'],
        'UC Berkeley': ['University of California', 'Berkeley', 'Regents of the University of California']
    }

    commercial_entities = {
        'Editas Medicine': ['Editas Medicine', 'Editas'],
        'CRISPR Therapeutics': ['CRISPR Therapeutics', 'CRISPR Therapeutics AG'],
        'Intellia Therapeutics': ['Intellia Therapeutics', 'Intellia']
    }

    all_patents = []
    assignee_stats = defaultdict(lambda: {'count': 0, 'patents': []})
    patent_families = defaultdict(list)
    geographic_coverage = defaultdict(int)
    litigation_indicators = []

    # Search for CRISPR-related patents
    print("Searching USPTO for CRISPR patents...")

    # Main CRISPR technology search
    search_terms = [
        'CRISPR',
        'CRISPR-Cas9',
        'CRISPR-Cas',
        'clustered regularly interspaced short palindromic repeats',
        'gene editing CRISPR'
    ]

    for term in search_terms:
        print(f"  Searching: {term}...")
        try:
            result = search_patents(
                query=term,
                limit=500  # Get comprehensive results
            )

            if result and 'patents' in result:
                patents = result['patents']
                all_patents.extend(patents)
                print(f"    Found {len(patents)} patents for '{term}'")
        except Exception as e:
            print(f"    Error searching '{term}': {e}")
            continue

    # Deduplicate patents by patent number
    unique_patents = {}
    for patent in all_patents:
        patent_num = patent.get('patentNumber') or patent.get('patent_number') or patent.get('id', '')
        if patent_num and patent_num not in unique_patents:
            unique_patents[patent_num] = patent

    all_patents = list(unique_patents.values())
    print(f"\nTotal unique CRISPR patents found: {len(all_patents)}")

    # Analyze each patent
    for patent in all_patents:
        # Extract patent details
        patent_num = patent.get('patentNumber') or patent.get('patent_number') or patent.get('id', '')
        title = patent.get('title', '')
        assignee = patent.get('assignee', '') or patent.get('assigneeName', '') or patent.get('owner', '')
        abstract = patent.get('abstract', '')
        filing_date = patent.get('filingDate') or patent.get('filing_date', '')
        grant_date = patent.get('grantDate') or patent.get('grant_date', '') or patent.get('issueDate', '')

        # Categorize by assignee
        assignee_category = 'Other'

        # Check academic entities
        for institution, keywords in academic_entities.items():
            if any(keyword.lower() in assignee.lower() for keyword in keywords):
                assignee_category = institution
                break

        # Check commercial entities
        if assignee_category == 'Other':
            for company, keywords in commercial_entities.items():
                if any(keyword.lower() in assignee.lower() for keyword in keywords):
                    assignee_category = company
                    break

        # Track assignee statistics
        assignee_stats[assignee_category]['count'] += 1
        assignee_stats[assignee_category]['patents'].append({
            'patent_number': patent_num,
            'title': title,
            'assignee': assignee,
            'filing_date': filing_date,
            'grant_date': grant_date
        })

        # Detect patent families (simplified - based on title similarity)
        base_title = re.sub(r'\s+(I{1,3}|IV|V|VI{1,3}|IX|X|[0-9]+)$', '', title)
        patent_families[base_title].append(patent_num)

        # Track geographic coverage (based on assignee location)
        if 'United States' in assignee or 'U.S.' in assignee or 'Massachusetts' in assignee or 'California' in assignee:
            geographic_coverage['United States'] += 1
        elif 'Europe' in assignee or 'Switzerland' in assignee or 'Germany' in assignee:
            geographic_coverage['Europe'] += 1
        elif 'Japan' in assignee or 'China' in assignee or 'Korea' in assignee:
            geographic_coverage['Asia'] += 1

        # Detect potential litigation indicators
        if any(keyword in abstract.lower() for keyword in ['interference', 'priority', 'dispute', 'challenge']):
            litigation_indicators.append({
                'patent_number': patent_num,
                'title': title,
                'assignee': assignee
            })

    # Prepare summary
    summary = {
        'total_patents': len(all_patents),
        'assignee_breakdown': {},
        'top_patent_families': [],
        'geographic_coverage': dict(geographic_coverage),
        'litigation_indicators_count': len(litigation_indicators)
    }

    # Sort assignees by patent count
    sorted_assignees = sorted(assignee_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    for assignee, stats in sorted_assignees:
        summary['assignee_breakdown'][assignee] = {
            'count': stats['count'],
            'percentage': round(stats['count'] / len(all_patents) * 100, 1) if all_patents else 0
        }

    # Identify top patent families
    sorted_families = sorted(patent_families.items(), key=lambda x: len(x[1]), reverse=True)
    for family_title, patents in sorted_families[:10]:
        if len(patents) > 1:  # Only include actual families
            summary['top_patent_families'].append({
                'family_title': family_title,
                'patent_count': len(patents),
                'patent_numbers': patents
            })

    # Print summary
    print("\n" + "="*80)
    print("CRISPR IP LANDSCAPE SUMMARY")
    print("="*80)
    print(f"\nTotal CRISPR Patents: {summary['total_patents']}")

    print("\nAssignee Breakdown:")
    print("-" * 60)
    for assignee, stats in sorted_assignees[:15]:
        print(f"  {assignee:40} {stats['count']:5} patents ({summary['assignee_breakdown'][assignee]['percentage']:5.1f}%)")

    if summary['top_patent_families']:
        print("\nTop Patent Families (by number of related patents):")
        print("-" * 60)
        for family in summary['top_patent_families'][:5]:
            print(f"  {family['family_title'][:70]:70} {family['patent_count']:3} patents")

    if geographic_coverage:
        print("\nGeographic Coverage:")
        print("-" * 60)
        for region, count in sorted(geographic_coverage.items(), key=lambda x: x[1], reverse=True):
            print(f"  {region:30} {count:5} patents")

    if litigation_indicators:
        print(f"\nPotential Litigation Indicators: {len(litigation_indicators)} patents")
        print("-" * 60)
        for indicator in litigation_indicators[:5]:
            print(f"  {indicator['patent_number']}: {indicator['title'][:60]}")
            print(f"    Assignee: {indicator['assignee']}")

    print("\nKey Academic Institutions:")
    print("-" * 60)
    for institution in ['Broad Institute', 'UC Berkeley']:
        if institution in assignee_stats:
            print(f"  {institution}: {assignee_stats[institution]['count']} patents")

    print("\nKey Commercial Entities:")
    print("-" * 60)
    for company in ['Editas Medicine', 'CRISPR Therapeutics', 'Intellia Therapeutics']:
        if company in assignee_stats:
            print(f"  {company}: {assignee_stats[company]['count']} patents")

    print("\n" + "="*80)

    return {
        'summary': summary,
        'detailed_assignee_data': dict(assignee_stats),
        'patent_families': dict(patent_families),
        'litigation_indicators': litigation_indicators
    }

if __name__ == "__main__":
    result = get_crispr_ip_landscape()
    print(f"\nAnalysis complete. Total patents analyzed: {result['summary']['total_patents']}")
