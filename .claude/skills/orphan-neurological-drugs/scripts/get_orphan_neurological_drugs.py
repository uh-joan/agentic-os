import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drugs
from datetime import datetime, timedelta

def get_orphan_neurological_drugs():
    """Get FDA orphan drug approvals for rare neurological diseases (past 3 years).
    
    Returns:
        dict: Contains total_count, drugs data, and summary
    """
    three_years_ago = datetime.now() - timedelta(days=3*365)
    
    neuro_queries = [
        "spinal muscular atrophy",
        "Duchenne muscular dystrophy",
        "amyotrophic lateral sclerosis",
        "Huntington disease",
        "multiple sclerosis",
        "epilepsy",
        "ataxia",
        "myasthenia gravis",
        "neuropathy",
        "neurodegenerative"
    ]
    
    all_results = []
    
    for query in neuro_queries:
        try:
            result = search_drugs(search=query, limit=50)
            if result and 'results' in result:
                all_results.extend(result['results'])
        except Exception as e:
            print(f"Warning: Error searching {query}: {e}")
    
    unique_drugs = {}
    for drug in all_results:
        openfda = drug.get('openfda', {})
        app_nums = openfda.get('application_number', [])
        
        if app_nums:
            app_num = app_nums[0]
            if app_num not in unique_drugs:
                unique_drugs[app_num] = drug
    
    recent_drugs = []
    
    for drug in unique_drugs.values():
        openfda = drug.get('openfda', {})
        
        approval_date = None
        submissions = drug.get('submissions', [])
        
        for submission in submissions:
            if submission.get('submission_status') == 'AP':
                date_str = submission.get('submission_status_date')
                if date_str:
                    try:
                        approval_date = datetime.strptime(date_str, "%Y%m%d")
                        if approval_date >= three_years_ago:
                            break
                    except:
                        pass
        
        if approval_date and approval_date >= three_years_ago:
            brand_names = openfda.get('brand_name', [])
            generic_names = openfda.get('generic_name', [])
            manufacturers = openfda.get('manufacturer_name', [])
            routes = openfda.get('route', [])
            product_types = openfda.get('product_type', [])
            
            drug_data = {
                'brand_name': brand_names[0] if brand_names else 'Unknown',
                'generic_name': generic_names[0] if generic_names else 'Unknown',
                'manufacturer': manufacturers[0] if manufacturers else 'Unknown',
                'application_number': openfda.get('application_number', ['Unknown'])[0],
                'approval_date': approval_date.strftime("%Y-%m-%d"),
                'approval_year': approval_date.year,
                'route': routes[0] if routes else 'Unknown',
                'product_type': product_types[0] if product_types else 'Unknown'
            }
            
            recent_drugs.append(drug_data)
    
    recent_drugs.sort(key=lambda x: x['approval_date'], reverse=True)
    
    total_count = len(recent_drugs)
    
    by_year = {}
    for drug in recent_drugs:
        year = str(drug['approval_year'])
        by_year[year] = by_year.get(year, 0) + 1
    
    by_manufacturer = {}
    for drug in recent_drugs:
        mfr = drug['manufacturer']
        by_manufacturer[mfr] = by_manufacturer.get(mfr, 0) + 1
    
    top_manufacturers = sorted(by_manufacturer.items(), key=lambda x: x[1], reverse=True)[:5]
    
    by_route = {}
    for drug in recent_drugs:
        route = drug['route']
        by_route[route] = by_route.get(route, 0) + 1
    
    summary = {
        'total_drugs': total_count,
        'date_range': f"{three_years_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
        'by_year': dict(sorted(by_year.items(), reverse=True)),
        'top_manufacturers': [{'name': m[0], 'count': m[1]} for m in top_manufacturers],
        'by_route': dict(sorted(by_route.items(), key=lambda x: x[1], reverse=True))
    }
    
    return {
        'total_count': total_count,
        'data': recent_drugs,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_orphan_neurological_drugs()
    
    print(f"\n{'='*80}")
    print(f"FDA Orphan Drugs - Rare Neurological Diseases (Past 3 Years)")
    print(f"{'='*80}\n")
    
    print(f"Total Approvals: {result['summary']['total_drugs']}")
    print(f"Date Range: {result['summary']['date_range']}\n")
    
    print("Approvals by Year:")
    for year, count in result['summary']['by_year'].items():
        print(f"  {year}: {count} drugs")
    
    print(f"\nTop 5 Manufacturers:")
    for mfr in result['summary']['top_manufacturers']:
        print(f"  {mfr['name']}: {mfr['count']} approvals")
    
    print(f"\nAdministration Routes:")
    for route, count in list(result['summary']['by_route'].items())[:5]:
        print(f"  {route}: {count} drugs")
    
    print(f"\n{'='*80}")
    print(f"Recent Approvals (Top 15):")
    print(f"{'='*80}\n")
    
    for i, drug in enumerate(result['data'][:15], 1):
        print(f"{i}. {drug['brand_name']} ({drug['generic_name']})")
        print(f"   Manufacturer: {drug['manufacturer']}")
        print(f"   Approved: {drug['approval_date']}")
        print(f"   Application: {drug['application_number']}")
        print(f"   Route: {drug['route']}")
        print()
    
    if result['total_count'] > 15:
        print(f"... and {result['total_count'] - 15} more approvals")
